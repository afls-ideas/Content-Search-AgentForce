public with sharing class ContentSearchAction {

    private static final Integer MAX_RESULTS = 3;
    private static final Integer CANDIDATES = 20;
    private static final Decimal MIN_SCORE = 0.2;

    public class Request {
        @InvocableVariable(label='Topic' description='The topic, question or keywords the user wants to find in presentation slides' required=true)
        public String topic;
    }

    public class Result {
        @InvocableVariable(label='Matches' description='Matching presentation slides, best match first, one per line, with a text excerpt')
        public String matches;
        @InvocableVariable(label='Match Count' description='Number of matching slides')
        public Integer matchCount;
    }

    @InvocableMethod(label='Search Presentation Slides' description='Searches the text of presentation slides with Data 360 hybrid search and returns the slides that best match a topic' callout=true)
    public static List<Result> search(List<Request> requests) {
        List<Result> results = new List<Result>();
        for (Request req : requests) {
            results.add(searchOne(req));
        }
        return results;
    }

    private static Result searchOne(Request req) {
        Result res = new Result();
        res.matchCount = 0;
        res.matches = 'No matching slides found.';
        if (req == null || String.isBlank(req.topic)) {
            return res;
        }

        String sql = 'SELECT h.hybrid_score__c AS score, c.SourceRecordId__c AS pageId, '
            + 'c.Chunk__c AS chunk, c.DataSource__c AS fld '
            + 'FROM hybrid_search(TABLE(Presentation_Page_index__dlm), \''
            + String.escapeSingleQuotes(req.topic) + '\', \'\', ' + CANDIDATES + ') h '
            + 'JOIN Presentation_Page_chunk__dlm c ON h.RecordId__c = c.RecordId__c';

        ConnectApi.CdpQueryInput input = new ConnectApi.CdpQueryInput();
        input.sql = sql;
        ConnectApi.CdpQueryOutputV2 output = ConnectApi.CdpQuery.queryAnsiSqlV2(input);

        // Best score per page, plus the page-text excerpt when the text field matched
        Map<String, Decimal> bestScore = new Map<String, Decimal>();
        Map<String, String> excerpt = new Map<String, String>();
        List<String> order = new List<String>();
        if (output != null && output.data != null) {
            for (Object rowObj : output.data) {
                List<Object> row = (List<Object>) JSON.deserializeUntyped(JSON.serialize(rowObj));
                Decimal score = row[0] == null ? 0 : Decimal.valueOf(String.valueOf(row[0]));
                String pageId = (String) row[1];
                // Only page-text matches count: page names are near-identical ("Immunexis ...") and match too broadly
                if (score < MIN_SCORE || pageId == null || (String) row[3] != 'ExtractedText__c') {
                    continue;
                }
                if (!bestScore.containsKey(pageId)) {
                    bestScore.put(pageId, score);
                    order.add(pageId);
                }
                if (!excerpt.containsKey(pageId)) {
                    String chunk = (String) row[2];
                    excerpt.put(pageId, chunk.abbreviate(1500));
                }
            }
        }
        if (order.isEmpty()) {
            return res;
        }

        Map<Id, PresentationPage> pages = new Map<Id, PresentationPage>(
            [SELECT Id, Name FROM PresentationPage WHERE Id IN :order]
        );
        List<String> lines = new List<String>();
        for (String pageId : order) {
            if (lines.size() >= MAX_RESULTS) {
                break;
            }
            PresentationPage pg = pages.get(pageId);
            if (pg == null) {
                continue;
            }
            String line = (lines.size() + 1) + '. ' + pg.Name + ' (Id: ' + pg.Id
                + ', relevance: ' + bestScore.get(pageId).setScale(2) + ')';
            if (excerpt.containsKey(pageId)) {
                line += ' - ' + excerpt.get(pageId);
            }
            lines.add(line);
        }
        if (!lines.isEmpty()) {
            res.matches = String.join(lines, '\n');
            res.matchCount = lines.size();
        }
        return res;
    }
}