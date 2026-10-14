/**
 * CLT data type backing the `presentationRecommendationCLT` custom
 * Lightning type.
 *
 * Top-level `global` + `@JsonAccess`, `@AuraEnabled global` fields — required
 * for the `@apexClassType` CLT binding to resolve when the type is declared
 * via an Agent Script `complex_data_type_name` output.
 */
@JsonAccess(serializable='always' deserializable='always')
global class PresentationRecommendationWrapper {
    @AuraEnabled global String slideName;
    @AuraEnabled global String presentationName;
    @AuraEnabled global Integer pageNumber;
    @AuraEnabled global String thumbnailUrl;
    @AuraEnabled global String matchReason;
}
