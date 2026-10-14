@JsonAccess(serializable='always' deserializable='always')
global class ShowSlideResult {
    @InvocableVariable(label='Slide' description='The slide, with its thumbnail, to display in the chat window')
    global PresentationRecommendationWrapper slide;

    @InvocableVariable(label='Summary' description='Plain-text summary of the slide shown')
    global String summary;
}
