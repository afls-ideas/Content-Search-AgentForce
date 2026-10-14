import base64, json, html
T = json.load(open("immunexis/extracted_text.json"))
slides = [("Immunexis Overview","01_Intro"),("Immunexis Efficacy","02_Efficacy"),("Immunexis Safety","03_Safety"),("Immunexis Dosing","04_Dosing"),("Immunexis Resources","05_PatientSupport")]
def img(f): return "data:image/jpeg;base64," + base64.b64encode(open(f"docs/img/{f}.jpg","rb").read()).decode()
cards = ""
for name, f in slides:
    cards += f"""<div class="card"><h3>{name}</h3><img src="{img(f)}" alt="{name} slide">
<details><summary>Transcribed text stored in Extracted_Text__c</summary><pre>{html.escape(T[name])}</pre></details></div>\n"""
results = [("What is the maintenance dose?","Immunexis Dosing","0.973"),("headache rate vs placebo","Immunexis Safety","0.967"),("IL-23","Immunexis Overview","0.967"),("remission at week 52","Immunexis Efficacy","1.000"),("co-pay savings card","Immunexis Resources","0.779")]
rows = "".join(f"<tr><td>{q}</td><td>{p}</td><td>{s}</td></tr>" for q,p,s in results)
page = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Searching Slide Images with Data 360 Hybrid Search</title>
<style>
body{{font-family:-apple-system,Helvetica,Arial,sans-serif;max-width:980px;margin:2rem auto;padding:0 1rem;color:#1d1d1f;line-height:1.55}}
h1{{border-bottom:3px solid #5b2a9d;padding-bottom:.4rem}} h2{{margin-top:2.2rem;color:#4a1a7a}}
code,pre{{background:#f4f1f8;border-radius:4px;font-size:.88em}} code{{padding:.1em .3em}} pre{{padding:.8rem;overflow:auto;white-space:pre-wrap}}
table{{border-collapse:collapse;width:100%;margin:1rem 0}} th,td{{border:1px solid #d6cfe3;padding:.45rem .6rem;text-align:left;vertical-align:top}} th{{background:#efe9f7}}
.card{{border:1px solid #d6cfe3;border-radius:8px;padding:1rem;margin:1.2rem 0}} .card img{{width:100%;border-radius:6px}}
.note{{background:#fff7e0;border-left:4px solid #e0a800;padding:.6rem .9rem;margin:1rem 0}}
.flow{{display:flex;flex-wrap:wrap;gap:.5rem;align-items:center;margin:1rem 0}} .flow span{{background:#5b2a9d;color:#fff;padding:.4rem .7rem;border-radius:6px;font-size:.9em}} .flow i{{font-style:normal;color:#5b2a9d}}
</style></head><body>
<h1>Searching Slide Images with Data 360 Hybrid Search</h1>
<p>Presentation slides in this org are stored as images inside zip files, so Data 360 has no text to index. This page documents how we turned the slide images into searchable text and verified that hybrid search returns the right slide. It was tested on one demo presentation (five slides, shown below).</p>

<h2>1. Architecture</h2>
<div class="flow"><span>Slide zip (ContentDocument)</span><i>→</i><span>Unzip, get PNG</span><i>→</i><span>Vision model transcribes text</span><i>→</i><span>PresentationPage.Extracted_Text__c</span><i>→</i><span>Data stream (DLO)</span><i>→</i><span>Presentation Page DMO</span><i>→</i><span>Hybrid search index</span></div>
<p>A search index can only chunk text fields on a data model object (DMO). The slide content lives in files, so the text has to be extracted first and stored on the record that the index is built on.</p>

<h2>2. The demo content</h2>
<p>Each Presentation Page in the demo presentation has a zip file holding one slide image (2464 &times; 1728 PNG), a thumbnail and a small HTML wrapper.</p>
{cards}

<h2>3. Setup steps</h2>
<h3>Step 1: Get the images</h3>
<p>For each page, find the latest <code>ContentVersion</code> of its <code>ContentDocumentId</code>, download <code>VersionData</code> (<code>sf api request rest ... --stream-to-file</code>) and unzip it. The slide is the PNG in <code>assets/</code>.</p>
<h3>Step 2: Extract the text</h3>
<p>We first tried OCR (macOS Vision). It was fast but flattened tables into loose lines, read "Phase III" as "Phase Ill", and dropped a number in the safety table (4.1% came out as 1%). We switched to a vision LLM, which transcribed each slide into structured text with the table rows rebuilt as "Adverse event: A vs B" lines. Garbled fine print was left out.</p>
<h3>Step 3: Add a long text field</h3>
<p>Create <code>PresentationPage.Extracted_Text__c</code> (Long Text Area, 32,768 characters). Grant field access through a permission set, because a new field created through the API is invisible to everyone until it has field-level security. Then write each page's transcript to the field.</p>
<h3>Step 4: Bring the field into Data 360</h3>
<ol>
<li>Open the <code>PresentationPage_Home</code> data stream and use <b>Add Source Fields</b> to add <code>Extracted_Text__c</code>.</li>
<li>The new column is named <code>Extracted_Text_c__c</code> in the data lake object (DLO).</li>
<li>Re-save the records and run the stream again. Refreshes are incremental, so rows that haven't changed since the field was added are not backfilled.</li>
</ol>
<div class="note">Rows without text arrive as empty strings, not NULL. Test with <code>LENGTH(col) &gt; 0</code> rather than <code>IS NOT NULL</code>.</div>
<h3>Step 5: Add the field to the standard DMO and map it</h3>
<p>The standard Presentation Page DMO has no long-text field, so we added a custom field <code>ExtractedText__c</code> to it and mapped <code>Extracted_Text_c__c</code> to it. (We first tried a separate custom DMO, but its index could not be created through the API, so we removed it.) Check the result with a query:</p>
<pre>SELECT ssot__Name__c, LENGTH(ExtractedText__c)
FROM ssot__PresentationPage__dlm
WHERE LENGTH(ExtractedText__c) &gt; 0</pre>
<h3>Step 6: Add the field to the search index</h3>
<ul>
<li>Search type: <b>Hybrid</b> (keyword plus vector).</li>
<li>Source DMO: Presentation Page. Chunked field: <code>Extracted Text</code>, passage extraction, 512 tokens.</li>
<li>Embedding model: <code>e5_large_v2</code> (1,024 dimensions, HNSW, cosine similarity).</li>
</ul>
<p>Rebuilding took about ten minutes (SUBMITTED, then IN_PROGRESS, then READY). The chunk table went from 82 name-only chunks to 87, which includes one chunk per transcribed slide.</p>

<h2>4. Querying</h2>
<pre>SELECT * FROM hybrid_search(TABLE(Presentation_Page_index__dlm), 'What is the maintenance dose?', '', 5)</pre>
<p>The result has <code>hybrid_score__c</code>, <code>keyword_score__c</code>, <code>vector_score__c</code> and a <code>RecordId__c</code>. Join <code>RecordId__c</code> to the chunk table to get the chunk text and the source page.</p>

<h2>5. Results</h2>
<table><tr><th>Query</th><th>Top hit</th><th>Hybrid score</th></tr>{rows}</table>
<p>All five queries returned the correct slide at rank 1. Each winning hit came from an <code>ExtractedText__c</code> chunk, except the dosing query, where the page-name chunk led by 0.006 over the text chunk. Keyword matching helps exact terms (<code>IL-23</code>) and the vector score helps paraphrases (<code>maintenance dose</code>). Below the top hit, scores fall to about 0.5&ndash;0.6 and are mostly page-name chunks with no keyword match.</p>
<p><b>Not tested:</b> the other pages (they have no extracted text), queries that should return nothing, and an Agentforce retriever on top of the index.</p>

<h2>6. Things that went wrong, and why</h2>
<table>
<tr><th>Symptom</th><th>Cause / fix</th></tr>
<tr><td>Creating a second index on the same source returns a generic <code>UNKNOWN_EXCEPTION</code></td><td>Only one index is allowed per source DMO (and attachment DMO). Delete or edit the existing index instead.</td></tr>
<tr><td>Index built only name chunks from file attachments</td><td>The slide PDFs are image-only with no text layer, so text extraction had nothing to read. This is why we transcribe to a text field.</td></tr>
<tr><td>Attachment join returned nothing</td><td>The ContentDocumentLink DLO had to be mapped manually to the Content Document Relationship DMO.</td></tr>
<tr><td><code>INVALID_FIELD</code> when writing the new field</td><td>No field-level security on the new field. Add it to a permission set.</td></tr>
<tr><td>Refresh ran but new field was empty in the DLO</td><td>Incremental refresh. Update the records so they change, then refresh again. One run also failed with "Cancelled before delete spark jobs" and had to be repeated.</td></tr>
<tr><td>Field not visible on the DMO</td><td>The standard Presentation Page DMO has no such field until you add one. Mapped DLO columns also get renamed (<code>Extracted_Text__c</code> becomes <code>Extracted_Text_c__c</code> in the DLO and <code>ExtractedText__c</code> on the DMO).</td></tr>
</table>
</body></html>"""
open("docs/immunexis_hybrid_search_setup.html","w").write(page)
