import { LightningElement, api, wire } from 'lwc';
import { CurrentPageReference } from 'lightning/navigation';

/**
 * Life Sciences example for the lightning__AgentforceOutput target: shows a
 * coworker-recommended presentation slide (deck name, slide name, page
 * number) alongside its thumbnail image, rendered from the slide's linked
 * JPG/PNG thumbnail file via the standard file rendition endpoint.
 *
 * See PresentationRecommendationWrapper for the Apex-side field names.
 * Follows the same dual Web/Mobile data path as the sampleAgentforceOutputLWC
 * template: Web sets the @api `value` property directly; the AFLS mobile app
 * instead resolves data via lightning/navigation's PageReference state params
 * (c__<FieldName>), only accepting them once c__channel === 'Mobile' marks
 * the page-ref as the real mobile payload rather than an unrelated re-fire.
 */
export default class PresentationRecommendationLWC extends LightningElement {
    _value = null;

    @api
    get value() {
        return this._value;
    }
    set value(val) {
        this._applyValue(val);
    }

    @wire(CurrentPageReference)
    wiredPageRef(pageRef) {
        if (this._value) return;

        const state = pageRef?.state;
        if (!state || state.c__channel !== 'Mobile') return;

        const slideName = this._parseStateParam(state.c__slideName);
        const presentationName = this._parseStateParam(state.c__presentationName);
        const pageNumber = this._parseStateParam(state.c__pageNumber);
        const thumbnailUrl = this._parseStateParam(state.c__thumbnailUrl);
        const matchReason = this._parseStateParam(state.c__matchReason);

        if (slideName == null && presentationName == null && pageNumber == null
            && thumbnailUrl == null && matchReason == null) {
            return;
        }

        this._applyValue({ slideName, presentationName, pageNumber, thumbnailUrl, matchReason });
    }

    _parseStateParam(raw) {
        if (raw === undefined || raw === null || raw === '') return null;
        if (typeof raw !== 'string') return raw;
        try {
            return JSON.parse(raw);
        } catch (e) {
            return raw;
        }
    }

    _applyValue(val) {
        this._value = val;
    }

    get _parsed() {
        if (!this._value) return null;
        if (typeof this._value === 'string') {
            try {
                return JSON.parse(this._value);
            } catch (e) {
                return null;
            }
        }
        return this._value;
    }

    get slideName() {
        return this._parsed?.slideName ?? '';
    }

    get presentationName() {
        return this._parsed?.presentationName ?? '';
    }

    get pageNumber() {
        return this._parsed?.pageNumber ?? '';
    }

    get thumbnailUrl() {
        return this._parsed?.thumbnailUrl ?? '';
    }

    get matchReason() {
        return this._parsed?.matchReason ?? '';
    }

    get hasData() {
        return !!this._parsed;
    }

    get hasThumbnail() {
        return !!this.thumbnailUrl;
    }
}
