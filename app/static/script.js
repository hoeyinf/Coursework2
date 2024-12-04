$(document).ready(function(){

    /* Cookies */
    window.addEventListener("load",function(){
        window.cookieconsent.initialise({
          "pallette":{
              "popup":{
                "background": "#eaf7f7",
                "text": "#5c7291"
              },
              "button":{
                "background":"#56cbdb",
                 "text": "#ffffff"
              }
            },
            "content": {
              "message": "This website uses cookies",
              "dismiss": "Got it!",
            }
        })});

    /* Button redirects */
    $(".edit-profile").click(function(){
        window.location.href = "/edit_profile";
    });

    /* Delete profile button */
    $(".delete-profile").click(function(e){
        if (confirm("Are you sure you want to delete your profile?")){
            window.location.href = "/delete_profile";
        }
    });

    /* Profile active content toggling */
    $(".following, .followers").hide();
    
    $("button.profile").click(function(){
        var action = $(this).attr("name");
        $("table").hide();
        if(action != "posts"){
            $("div.posts").hide();
            $("table."+action).show();
        }else{
            $("div.posts").show();
        }
        $("button.profile").removeClass("active");
        $("button.profile").attr("aria-pressed", "false");
        $(this).addClass("active");
        $(this).attr("aria-pressed", "true");
    });

    /* Redirect to view book when div is clicked
    Learned from: https://stackoverflow.com/questions/10851312/document-click-not-in-elements-jquery*/
    $("div.book-info").click(function(e){
        var id = $(this).attr("id");
        if(!$(e.target).is("button")){
            $(this).parent().children("button[value="+id+"]").trigger("click");
        }
    });

    /* So that highlighted div can be clicked on 'Enter' press */
    $(document).on('keydown','div.book-info',function(e){
        if(e.which==13)
            $(this).click()
    });
});