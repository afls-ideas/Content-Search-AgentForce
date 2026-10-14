@JsonAccess(serializable='always' deserializable='always')
global class ShowSlideRequest {
    @InvocableVariable(label='Slide Id' description='The Id of the presentation slide to show, taken from the Search Presentation Slides results' required=true)
    global String pageId;
}
