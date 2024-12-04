$(document).ready(function () {

    /* Add/remove book from user's reading list */
    $(".edit-reading-list").click(function () {
        $.ajax({
            // Specify the endpoint URL the request should be sent to.
            url: '/edit_reading_list',
            // The request type.
            type: 'POST',
            // The data, which is now most commonly formatted using JSON because of its
            // simplicity and is native to JavaScript.
            data: JSON.stringify({ id: $(this).attr("id"), action: $(this).attr("name") }),
            // Specify the format of the data which will be sent.
            contentType: "application/json; charset=utf-8",
            // The data type itself.
            dataType: "json",
            // Define the function which will be triggered if the request is received and
            // a response successfully returned.
            success: function (response) {

                // Switch the button when not viewing reading_list.html
                if ($('#' + response.id).attr("name") == 'add') {
                    $('#' + response.id).html("Remove from Reading List");
                    $('#' + response.id).attr("name", "remove")
                    $(".list-change").text("'" + response.title + "' added to reading list!")
                } else if ($(document).attr('title') != 'Reading List') {
                    $('#' + response.id).html("Add to Reading List");
                    $('#' + response.id).attr("name", "add")
                    $(".list-change").text("'" + response.title + "' removed from reading list.")
                } else {
                    // Stop displaying book on reading list
                    $('#' + response.id).parent().parent().fadeOut(600);
                    $(".list-change").text("'" + response.title + "' removed from reading list.")
                }
                $(".list-change").parent().show();
                $(".list-change").parent().delay(2000).fadeOut(200)
            },
            // The function which will be triggered if any error occurs.
            error: function (error) {
                console.log(error);
            }
        });

    });

    /* Follow/unfollow user */
    $(".edit-following").click(function () {
        $.ajax({
            url: '/edit_following',
            type: 'POST',
            data: JSON.stringify({ id: $(this).attr("id"), action: $(this).attr("name"), other: $(this).parent().attr('class') }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (response) {

                // Retrieve following/followers count (depending on where they clicked the unfollow button)
                const followersArray = $("[name='followers']").text().split(" ");
                const followingArray = $("[name='following']").text().split(" ");
                if (response.own_profile == true) {
                    var follow = Number(followingArray[1]);
                } else {
                    var follow = Number(followersArray[1]);
                }
                // Switch the button and change tables
                if ($('#follower-' + response.id + ', #following-' + response.id + ', #' + response.id).attr("name") == 'follow') {
                    $('#follower-' + response.id + ', #following-' + response.id + ', #' + response.id).html("Unfollow");
                    $('#follower-' + response.id + ', #following-' + response.id + ', #' + response.id).attr("name", "unfollow");
                    $(".list-change").text("Followed @" + response.username);
                    follow = follow + 1;
                    $('.' + response.id).show();
                } else {
                    $('#follower-' + response.id + ', #following-' + response.id + ', #' + response.id).html("Follow");
                    $('#follower-' + response.id + ', #following-' + response.id + ', #' + response.id).attr("name", "follow");
                    $(".list-change").text("Unfollowed @" + response.username);
                    follow = follow - 1;
                    $('.' + response.id).hide();
                }

                // Update following/followers count
                if (response.own_profile == true) {
                    $("[name='following']").children("strong").text(follow);
                } else {
                    $("[name='followers']").children("strong").text(follow);
                }

                // Show alert
                $(".list-change").parent().show();
                $(".list-change").parent().delay(2000).fadeOut(200);
            },
            error: function (error) {
                console.log(error);
            }
        });

    });

    /* Create post */
    $(".post-book").click(function () {
        $.ajax({
            url: '/post_book',
            type: 'POST',
            data: JSON.stringify({ id: $(this).attr("id") }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (response) {

                // Switch the button and display alert
                $("#mark-" + response.id).html("Book Finished!");
                $("#mark-" + response.id).attr('disabled', '');
                $(".list-change").text("Finished '" + response.title + "'! Post created.");
                $(".list-change").parent().show();
                $(".list-change").parent().delay(4000).fadeOut(200);
            },
            error: function (error) {
                console.log(error);
            }
        });
    });

    /* Delete post */
    $(".delete-book").click(function () {
        if (confirm("Are you sure you want to delete this post? This will mark the book unfinished.")) {
            $.ajax({
                url: '/delete_book',
                type: 'POST',
                data: JSON.stringify({ id: $(this).attr("id")}),
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                success: function (response) {
                    alert(response.alert);
                    window.location.href = "/";
                },
                error: function (error) {
                    console.log(error);
                }
            });
        }
    });

    /* Like/unlike post */
    $(".like-button").click(function () {
        $.ajax({
            url: '/like_post',
            type: 'POST',
            data: JSON.stringify({ id: $(this).attr("id"), action: $(this).attr("name") }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (response) {

                // Change like button and update count
                var likes = Number($("#" + response.id).html().slice(-1));
                if ($("#" + response.id).attr("name") == "like") {
                    $("#" + response.id).removeClass("btn-outline-primary").addClass("btn-primary");
                    $("#" + response.id).attr("name", "unlike");
                    $("#" + response.id).attr("aria-pressed", "true");
                    likes = likes + 1;
                } else {
                    $("#" + response.id).addClass("button-outline-primary");
                    $("#" + response.id).removeClass("btn-primary").addClass("btn-outline-primary");
                    $("#" + response.id).attr("name", "like");
                    $("#" + response.id).attr("aria-pressed", "false");
                    likes = likes - 1;
                }
                $("#" + response.id).html("<em class='fa fa-thumbs-up'></em> " + likes);
            },
            error: function (error) {
                console.log(error);
            }
        });
    });

});