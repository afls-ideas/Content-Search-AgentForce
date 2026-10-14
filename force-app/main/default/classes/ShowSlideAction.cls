/**
 * Shows a presentation slide inline in the agent chat. Returns the slide's
 * name, deck and thumbnail for the presentationRecommendationCLT renderer.
 * Top-level global + @JsonAccess is what lets the @apexClassType binding resolve.
 */
@JsonAccess(serializable='always' deserializable='always')
global class ShowSlideAction {

    private static final String THUMBNAIL_RENDITION = 'THUMB720BY480';

    @InvocableMethod(label='Show Presentation Slide' description='Shows a presentation slide and its thumbnail image inline in the chat')
    global static List<ShowSlideResult> show(List<ShowSlideRequest> requests) {
        List<ShowSlideResult> results = new List<ShowSlideResult>();
        for (ShowSlideRequest req : requests) {
            results.add(showOne(req));
        }
        return results;
    }

    private static ShowSlideResult showOne(ShowSlideRequest req) {
        ShowSlideResult res = new ShowSlideResult();
        List<PresentationPage> pages = String.isBlank(req.pageId) ? new List<PresentationPage>() : [
            SELECT Id, Name, PageNumber FROM PresentationPage WHERE Id = :req.pageId LIMIT 1
        ];
        if (pages.isEmpty()) {
            res.summary = 'That slide could not be found or you do not have access to it.';
            return res;
        }
        PresentationPage page = pages[0];

        PresentationRecommendationWrapper slide = new PresentationRecommendationWrapper();
        slide.slideName = page.Name;
        slide.pageNumber = page.PageNumber != null ? page.PageNumber.intValue() : null;
        slide.thumbnailUrl = findThumbnailUrl(page.Id);

        List<PresentationLinkedPage> links = [
            SELECT Presentation.Name FROM PresentationLinkedPage WHERE PresentationPageId = :page.Id LIMIT 1
        ];
        if (!links.isEmpty() && links[0].Presentation != null) {
            slide.presentationName = links[0].Presentation.Name;
        }

        res.slide = slide;
        res.summary = 'Showing slide "' + page.Name + '".';
        return res;
    }

    // Absolute URL (org My Domain + file rendition path). A relative /sfc/... URL has no host in the mobile app, and an
    // inline base64 image made the response large enough that the mobile app hung on "Loading the slide...".
    private static String findThumbnailUrl(Id presentationPageId) {
        List<ContentDocumentLink> thumbnailLinks = [
            SELECT ContentDocument.LatestPublishedVersionId
            FROM ContentDocumentLink
            WHERE LinkedEntityId = :presentationPageId
            AND ContentDocument.FileType IN ('JPG', 'JPEG', 'PNG')
            LIMIT 1
        ];
        if (thumbnailLinks.isEmpty()) {
            return null;
        }
        return URL.getOrgDomainUrl().toExternalForm() + '/sfc/servlet.shepherd/version/renditionDownload?rendition='
            + THUMBNAIL_RENDITION + '&versionId=' + thumbnailLinks[0].ContentDocument.LatestPublishedVersionId;
    }
}