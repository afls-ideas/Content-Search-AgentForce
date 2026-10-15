import json, subprocess, os, glob, datetime
O, N = os.environ["SF_ORG"], "Content_Recommendation_Agent"  # org alias via SF_ORG
env = dict(os.environ, SFDX_DISABLE_DNS_CHECK="true")
def sf(*a):
    for attempt in range(3):   # transient CLI/session errors happen under parallel load
        r = subprocess.run(["sf", "agent", "preview", *a, "-o", O, "-n", N, "--json"], capture_output=True, text=True, env=env)
        try:
            d = json.loads(r.stdout[r.stdout.index("{"):])
            if "result" in d: return d
        except ValueError: pass
    raise RuntimeError(f"sf agent preview {a[0]} failed: {r.stdout[-300:]}")
def trace_calls(sid, n_before):
    fs = sorted(glob.glob(f".sfdx/agents/*/sessions/{sid}/traces/*.json"), key=os.path.getmtime)
    calls = []
    for f in fs[n_before:]:
        for s in json.load(open(f))["plan"]:
            if s.get("type") == "FunctionStep":
                fn = s["function"]; calls.append((fn["name"], fn.get("input"), str(fn.get("output", {}).get("matches", ""))))
    return calls
# (id, category, turns[list of utterances], expected substrings (any) in final reply, expected action in last turn, forbidden substrings)
CASES = [
 ("T01","Dosing (slide-style)",["Which slide talks about the maintenance dose?"],["Immunexis Dosing"],"search_slides",[]),
 ("T02","Dosing (user report)",["where should I administer the drug?"],["Immunexis Dosing"],"search_only",["could not find","did not find"]),
 ("T03","Dosing",["What is the loading dose?"],["Immunexis Dosing"],"search_slides",[]),
 ("T04","Dosing",["how should the medication be stored?"],["Immunexis Dosing"],"search_only",[]),
 ("T05","Dosing",["can patients inject at home?"],["Immunexis Dosing"],"search_slides",[]),
 ("T06","Efficacy",["Which slide shows the clinical remission rate?"],["Immunexis Efficacy"],"search_slides",[]),
 ("T07","Efficacy",["how fast does it start working?"],["Immunexis Efficacy"],"search_slides",[]),
 ("T08","Safety",["what are the side effects?"],["Immunexis Safety"],"search_slides",[]),
 ("T09","Safety",["injection site reaction rates compared to placebo"],["Immunexis Safety"],"search_slides",[]),
 ("T10","Overview",["how does the drug work? mechanism of action"],["Immunexis Overview"],"search_slides",[]),
 ("T11","Patient support",["is there a co-pay savings card for patients?"],["Immunexis Resources"],"search_only",[]),
 ("T12","Patient support",["Where do I find prescribing information?"],["Immunexis Resources"],"search_slides",[]),
 ("T13","Show slide (multi-turn)",["Which slide talks about the maintenance dose?","show me the first slide"],["Dosing"],"show_slide",[]),
 ("T18","Confirm then show (multi-turn)",["where should I administer the drug?","yes"],["Immunexis Dosing"],"show_slide",[]),
 ("T14","Non-Immunexis content",["which slide covers statins and LDL cholesterol?"],[],"search_slides",[]),
 ("T15","No match",["which slide talks about the migration patterns of arctic terns?"],["no matching","couldn't find","could not find","did not find","no slides","not find"],"search_slides",[]),
 ("T16","Off-topic",["what's the weather in London today?"],["only help","presentation","slide"],None,[]),
 ("T17","Off-topic",["write me a poem about cats"],["only help","presentation","slide"],None,[]),
]
def run(case):
    cid, cat, turns, exp, act, forbid = case
    sid = sf("start")["result"]["sessionId"]
    reply, calls = "", []
    for i, u in enumerate(turns):
        before = len(glob.glob(f".sfdx/agents/*/sessions/{sid}/traces/*.json"))
        reply = sf("send", "-u", u, "--session-id", sid)["result"]["messages"][0]["message"]
        calls = trace_calls(sid, before)
    try: sf("end", "--session-id", sid)
    except RuntimeError: pass   # cleanup only
    names = [c[0] for c in calls]
    if act == "search_only":   # must search and must NOT display a slide before the user confirms
        ok_act = "search_slides" in names and "show_slide" not in names
    else:
        ok_act = (act in names) if act else not names
    low = reply.lower()
    SLIDES = ["immunexis overview", "immunexis efficacy", "immunexis safety", "immunexis dosing", "immunexis resources"]
    import re
    id2name = {m[1]: m[0].lower() for c in calls for m in re.findall(r"\d+\. (.+?) \(Id: (\w+)", c[2])}
    shown = [id2name.get(c[1].get("pageId")) for c in calls if c[0] == "show_slide" and c[1]]
    if exp and exp[0].lower() in SLIDES and shown and shown[-1]:   # slide displayed: judge by the slide actually shown
        ok_exp = shown[-1] == exp[0].lower()
    elif exp and exp[0].lower() in SLIDES:   # expected slide must be the FIRST slide named in the reply
        pos = {x: low.find(x) for x in SLIDES if x in low}
        ok_exp = bool(pos) and min(pos, key=pos.get) == exp[0].lower()
    else:
        ok_exp = (not exp) or any(e.lower() in low for e in exp)
    if act == "search_only": ok_exp = ok_exp and ("?" in reply)
    ok_forbid = not any(f in low for f in forbid + [" may ", "likely", "possibly", "might "] + (["see this slide", "view this slide", "show this slide", "like to see", "like me to show"] if act == "show_slide" else []))
    status = "PASS" if (ok_act and ok_exp and ok_forbid) else "FAIL"
    print(cid, status, names, flush=True)
    return (cid, cat, turns, exp, act, status, reply, calls)
from concurrent.futures import ThreadPoolExecutor
rows = list(ThreadPoolExecutor(4).map(run, CASES))
with open("agent_test_results.md", "w") as f:
    p = sum(r[5] == "PASS" for r in rows)
    f.write(f"# Content Recommendation Agent - utterance test results\n\nRun: {datetime.datetime.now():%Y-%m-%d %H:%M} | Org: `{O}` | Agent: `{N}` | Result: **{p}/{len(rows)} passed**\n\n")
    f.write("Pass = expected action called in the final turn AND the reply (or search result) mentions the expected slide AND no forbidden 'not found' phrasing.\n\n| ID | Category | Utterance(s) | Expected | Action called | Result |\n|---|---|---|---|---|---|\n")
    for cid, cat, turns, exp, act, st, reply, calls in rows:
        f.write(f"| {cid} | {cat} | {' -> '.join(turns)} | {' / '.join(exp) or '(any)'} | {', '.join(c[0] for c in calls) or 'none'} | **{st}** |\n")
    f.write("\n## Details\n")
    for cid, cat, turns, exp, act, st, reply, calls in rows:
        f.write(f"\n### {cid} - {st} - {cat}\n- **Utterance(s):** {' -> '.join(turns)}\n- **Expected action:** {act}\n")
        for n, i, m in calls: f.write(f"- **{n}** input `{json.dumps(i)}`" + (f" -> `{m[:400]}`" if m else "") + "\n")
        f.write(f"- **Reply:** {reply.strip()}\n")
