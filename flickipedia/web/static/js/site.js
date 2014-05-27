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

    var onLinkGlyph = [];
    var onLikeGlyph = [];
    var isEndorsed = [];
    var isExcluded = [];

    /**
     *  Handle hover events on the title image
     */
    this.titleImageHover = function() {
        $("div.title-image").hover(function() {
        }, function() {
        });
    };

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

            if (!onLikeGlyph[idx]) {

                var endorseGlyph = $(this).find("div.endorse");
                var excludeGlyph = $(this).find("div.reject");

                var imgEndorse = '<img style="float:left; opacity:0.4; background-color:#cccccc;" src="/static/img/endorse.png" width="25" height="25">';
                var imgExclude = '<img style="float:left; opacity:0.4; background-color:#cccccc;" src="/static/img/unendorse.png" width="25" height="25">';

                // Determine whether this user likes the photo
                $.getJSON('rest/api_photo_like_fetch' + '?' + params, function(data) {
                    isEndorsed[idx] = parseInt(data['like-fetch']);
                });
                $.getJSON('rest/api_photo_exclude_fetch' + '?' + params, function(data) {
                    isExcluded[idx] = parseInt(data['like-fetch']);
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

            if (!onLikeGlyph[idx]) {
                var endorseGlyph = $(this).find("div.endorse");
                var rejectGlyph = $(this).find("div.exclude");

                endorseGlyph[0].innerHTML = '';
                rejectGlyph[0].innerHTML = '';
            }
        });
    };

    /**
     *  Handle hover events on the like glyphs
     */
    this.likeGlyphImageHover = function(idx) {
        $("#like-glyph-" + idx).hover(function() {
            if (!onLikeGlyph[idx]) {
                var imgEndorse = '<img style="float:left; opacity:0.6; background-color:#cccccc;" src="/static/img/endorse.png" width="25" height="25">';
                var imgExclude = '<img style="float:left; opacity:0.6; background-color:#cccccc;" src="/static/img/unendorse.png" width="25" height="25">';

                var endorseGlyph = $(this).find("div.endorse");
                var excludeGlyph = $(this).find("div.exclude");

                endorseGlyph[0].innerHTML = imgEndorse;
                excludeGlyph[0].innerHTML = imgExclude;

                onLikeGlyph[idx] = true;
            }
        }, function() {
            var endorseGlyph = $(this).find("div.endorse");
            var rejectGlyph = $(this).find("div.reject");

            endorseGlyph[0].innerHTML = '';
            rejectGlyph[0].innerHTML = '';

            onLikeGlyph[idx] = false;
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
            $.getJSON('rest/api_photo_exclude_event' + method + '?' + params, function(data) {
                isEndorsed[idx] = isEndorsed[idx] ? false : true;
            });
        });
    };

    /**
     * Handle click events on the reject glyph. These events will allow users to toggle
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

    for (var i = 0; i < numPhotos; i++) {
        onLikeGlyph[i] = false;
        onLinkGlyph[i] = false;

        isEndorsed[i] = false;
        isExcluded[i] = false;

        this.sectionImageHover(i, 'photo-id=' + photos[i] + '&article-id=' + article + '&user-id=' + user);
        this.likeGlyphImageHover(i);
        this.endorseGlyphImageClick(i, 'photo-id=' + photos[i] + '&article-id=' + article + '&user-id=' + user);
        this.excludeGlyphImageClick(i, 'photo-id=' + photos[i] + '&article-id=' + article + '&user-id=' + user);
    }
}

