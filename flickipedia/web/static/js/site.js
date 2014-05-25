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
    var isLiked = [];

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
     * @param method
     * @param params
     */
    this.sectionImageHover = function(idx, method, params) {
        $("#" + sectionImageHandle + "-" + idx).hover(function() {

            var linkGlyph = $(this).find("a");
            linkGlyph[0].innerHTML = '<img style="opacity:0.8; background-color:#cccccc;" src="/static/img/link.png" width="25" height="25">';

            if (!onLikeGlyph[idx]) {

                // var likeGlyph = $(this).find("div.like-glyph");
                var endorseGlyph = $(this).find("div.endorse");
                var rejectGlyph = $(this).find("div.reject");

                var imgEndorse = '<img style="float:left; opacity:0.4; background-color:#cccccc;" src="/static/img/endorse.png" width="25" height="25">';
                var imgReject = '<img style="float:left; opacity:0.4; background-color:#cccccc;" src="/static/img/unendorse.png" width="25" height="25">';

                // Determine whether this user likes the photo
                $.getJSON('rest/' + method + '?' + params, function(data) {
                    isLiked[idx] = parseInt(data['like-fetch']);
                });
                if (isLiked[idx]) {
                    imgEndorse = '<img style="float:left; opacity:0.7; background-color:#cccccc;" src="/static/img/endorse.png" width="25" height="25">';
                    // likeGlyph[0].innerHTML = img_endorse + img_reject;
                } else {
                    // likeGlyph[0].innerHTML = img_endorse + img_reject;
                }
                endorseGlyph[0].innerHTML = imgEndorse;
                rejectGlyph[0].innerHTML = imgReject;
            }
        }, function() {
            var linkGlyph = $(this).find("a");
            linkGlyph[0].innerHTML = '<img style="opacity:0.4; background-color:#cccccc;" src="/static/img/link.png" width="25" height="25">';

            if (!onLikeGlyph[idx]) {
                // var likeGlyph = $(this).find("div.like-glyph");
                var endorseGlyph = $(this).find("div.endorse");
                var rejectGlyph = $(this).find("div.reject");

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
                var imgReject = '<img style="float:left; opacity:0.6; background-color:#cccccc;" src="/static/img/unendorse.png" width="25" height="25">';

                var endorseGlyph = $(this).find("div.endorse");
                var rejectGlyph = $(this).find("div.reject");

                endorseGlyph[0].innerHTML = imgEndorse;
                rejectGlyph[0].innerHTML = imgReject;

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
     * Handle click events on the like glyph. These events will allow users to toggle
     * whether they endorse the photo for inclusion
     *
     * @param idx       int, index on this article
     * @param method
     * @param params
     */
    this.likeGlyphImageClick = function(idx, method, params) {
        $("#like-glyph-" + idx).click(function() {
            $.getJSON('rest/' + method + '?' + params, function(data) {
                isLiked[idx] = isLiked[idx] ? false : true;
            });
        });
    };

    for (var i = 0; i < numPhotos; i++) {
        onLikeGlyph[i] = false;
        onLinkGlyph[i] = false;
        isLiked[i] = false;

        this.sectionImageHover(i, 'api_photo_like_fetch',
            'photo-id=' + photos[i] + '&article-id=' + article + '&user-id=' + user);
        this.likeGlyphImageHover(i);
        this.likeGlyphImageClick(i, 'api_photo_like_event',
            'photo-id=' + photos[i] + '&article-id=' + article + '&user-id=' + user);
    }
}

