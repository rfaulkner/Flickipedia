/**
 *  Flickipedia Site javascript
 *
 *  Ryan Faulkner 2014
 */


/**
 * Class object for handling callback code
 *
 * @param photos
 * @param article
 * @param user
 * @param numPhotos
 * @param sectionImageHandle
 * @constructor
 */
function InitPageCallbacks(
    photos,
    article,
    user,
    numPhotos,
    sectionImageHandle) {

    var onLinkGlyph = [];   // Flags indicating when hovering over "link" glyph
    var onVoteGlyph = [];   // Flags indicating when hovering over "vote" glyph
    var isEndorsed = [];    // Flags indicating which photos have been endorsed
    var isExcluded = [];    // Flags indicating which photos have been excluded


    /**
     * Handle hover events on the section images
     *
     * @param idx
     * @param params
     */
    this.sectionImageHover = function(idx, params) {
        $("#" + sectionImageHandle + "-" + idx).hover(function() {

            var linkGlyph = $(this).find("a");
            linkGlyph[0].innerHTML = '<img style="opacity:0.8; background-color:#cccccc;" src="/static/img/link.png" width="25" height="25">';

            if (!onVoteGlyph[idx]) {

                var endorseGlyph = $(this).find("div.endorse");
                var excludeGlyph = $(this).find("div.exclude");

                var imgEndorse = '<img style="float:left; opacity:0.4; background-color:#cccccc;" src="/static/img/endorse.png" width="25" height="25">';
                var imgExclude = '<img style="float:left; opacity:0.4; background-color:#cccccc;" src="/static/img/unendorse.png" width="25" height="25">';

                // Determine whether this user likes the photo
                $.getJSON('rest/api_photo_like_fetch' + '?' + params, function(data) {
                    isEndorsed[idx] = parseInt(data['endorse-fetch']);
                });
                $.getJSON('rest/api_photo_exclude_fetch' + '?' + params, function(data) {
                    isExcluded[idx] = parseInt(data['exclude-fetch']);
                });

                if (isEndorsed[idx]) {
                    imgEndorse = '<img style="float:left; opacity:0.7; background-color:#cccccc;" src="/static/img/endorse.png" width="25" height="25">';
                }

                if (isExcluded[idx]) {
                    imgExclude = '<img style="float:left; opacity:0.7; background-color:#cccccc;" src="/static/img/unendorse.png" width="25" height="25">';
                }
                endorseGlyph[0].innerHTML = imgEndorse;
                excludeGlyph[0].innerHTML = imgExclude;
            }
        }, function() {
            var linkGlyph = $(this).find("a");
            linkGlyph[0].innerHTML = '<img style="opacity:0.4; background-color:#cccccc;" src="/static/img/link.png" width="25" height="25">';

            if (!onVoteGlyph[idx]) {
                var endorseGlyph = $(this).find("div.endorse");
                var exludeGlyph = $(this).find("div.exclude");

                endorseGlyph[0].innerHTML = '';
                exludeGlyph[0].innerHTML = '';
            }
        });
    };

    /**
     *  Handle hover events on the like glyphs
     */
    this.voteGlyphImageHover = function(idx) {
        $("#vote-glyph-" + idx).hover(function() {
            if (!onVoteGlyph[idx]) {
                var imgEndorse = '<img style="float:left; opacity:0.6; background-color:#cccccc;" src="/static/img/endorse.png" width="25" height="25">';
                var imgExclude = '<img style="float:left; opacity:0.6; background-color:#cccccc;" src="/static/img/unendorse.png" width="25" height="25">';

                var endorseGlyph = $(this).find("div.endorse");
                var excludeGlyph = $(this).find("div.exclude");

                endorseGlyph[0].innerHTML = imgEndorse;
                excludeGlyph[0].innerHTML = imgExclude;

                onVoteGlyph[idx] = true;
            }
        }, function() {
            var endorseGlyph = $(this).find("div.endorse");
            var excludeGlyph = $(this).find("div.exclude");

            endorseGlyph[0].innerHTML = '';
            excludeGlyph[0].innerHTML = '';

            onVoteGlyph[idx] = false;
        });
    };

    /**
     * Handle click events on the endorse glyph. These events will allow users to toggle
     * whether they endorse the photo for inclusion
     *
     * @param idx       int, index on this article
     * @param params
     */
    this.endorseGlyphImageClick = function(idx, params) {
        $("#endorse-" + idx).click(function() {
            $.getJSON('rest/api_photo_exclude_event' + '?' + params, function(data) {
                isEndorsed[idx] = isEndorsed[idx] ? false : true;
            });
        });
    };

    /**
     * Handle click events on the exclude glyph. These events will allow users to toggle
     * whether they endorse the photo for exclusion
     *
     * @param idx       int, index on this article
     * @param params
     */
    this.excludeGlyphImageClick = function(idx, params) {
        $("#exclude-" + idx).click(function() {
            $.getJSON('rest/api_photo_exclude_event' + '?' + params, function(data) {
                isEndorsed[idx] = isEndorsed[idx] ? false : true;
            });
        });
    };

    /**
     * Iterate over all photos selected for the article and initialize data structures
     * & call back functions
     */
    for (var i = 0; i < numPhotos; i++) {
        onVoteGlyph[i] = false;
        onLinkGlyph[i] = false;

        isEndorsed[i] = false;
        isExcluded[i] = false;

        this.sectionImageHover(i, 'photo-id=' + photos[i] + '&article-id=' + article + '&user-id=' + user);
        this.voteGlyphImageHover(i);
        this.endorseGlyphImageClick(i, 'photo-id=' + photos[i] + '&article-id=' + article + '&user-id=' + user);
        this.excludeGlyphImageClick(i, 'photo-id=' + photos[i] + '&article-id=' + article + '&user-id=' + user);
    }
}

