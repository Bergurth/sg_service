

     $("#login-button").click(_.bind(__onLoginLinkClicked));
     $('.signup-ctrls').hide();
     $('.password-reset-ctrls').hide();
     $('.update-ctrls').hide();
     $('.get-ugames-ctrls').hide();

     $("#signup-link").click(_.bind(__onSignupLinkClicked));
     $("#update-link").click(_.bind(__onUpdateLinkClicked));
     $("#signin-link").click(_.bind(__onLoginLinkClicked));

     $("#banner-update-link").click(_.bind(__onUpdateBannerLinkClicked));
     $("#banner-ugame-link").click(_.bind(__onUgameBannerLinkClicked));

     $signupBtn = $("#signup-submit");
     $signinBtn = $("#signin-submit");
     $updateBtn = $("#update-submit");
     $ugameBtn  = $("#ugame-submit");

     //var server_url = "http://localhost:12315"
     var server_url = "http://sgtest.bergur.biz";

     $("#user-index-link").attr("href", server_url);

     var url1      = window.location.href;
     //location = window.location.href;
     var source_url = server_url +"/auth/logout?from_page="+url1;
     $('#logout_link').attr("href", source_url);


     $(".auth-form").submit(_.bind(this.__onFormSubmitted, this));
     $(".btn-login").click(_.bind(__onLoginButtonClicked));
     $('#password-reset-link').click(_.bind(__onPasswordResetLinkClicked));
     $('#cancel-reset-link').click(_.bind(__onLoginLinkClicked));

     function __onLoginLinkClicked(event) {
         $('.signup-ctrls').hide();
         $('.password-reset-ctrls').hide();
         $('.update-ctrls').hide();
         $('.get-ugames-ctrls').hide();
         $('.signin-ctrls').fadeIn()
          console.log("__onModalShown")
          $('div.signin-ctrls [name=username]').focus();
      }

      function __onUgameBannerLinkClicked(event){
        //$("#ugames-uname").val()
        $('.signup-ctrls').hide();
         $('.password-reset-ctrls').hide();
         $('.signin-ctrls').hide();
         $('.update-ctrls').hide();
        $("#auth-form-modal").modal('show');
        $('.get-ugames-ctrls').fadeIn();
        $('div.get-ugames-ctrls [name=username]').focus();
      }

      function getUgame(){
        var username = $("#ugames-uname").val();
        var url = server_url + "/user/?username="+username;
        window.location.href = url;
      }


      function __onUpdateBannerLinkClicked(event){
        $('.signup-ctrls').hide();
         $('.password-reset-ctrls').hide();
         $('.signin-ctrls').hide();
         $('.get-ugames-ctrls').hide();
        $("#auth-form-modal").modal('show');
        $('.update-ctrls').fadeIn();
        $('div.update-ctrls [name=username]').focus();
      }

      function __onFormSubmitted(event) {
          event.preventDefault();

          var $source = $(event.currentTarget);

          if ($signinBtn.is(':visible'))
              submitAsSignIn($source);
          else if ($signupBtn.is(':visible'))
              submitAsSignUp($source);
          else if ($updateBtn.is(':visible'))
              submitAsUpdate($source);
          else if ($ugameBtn.is(':visible'))
                getUgame();

          else {
              $('#password-reset-loader').show();
              submitAsReset($source);
          }
      }

      function __onPasswordResetLinkClicked(event) {
          event.preventDefault();

          $('.signin-ctrls, .signup-ctrls, .get-ugames-ctrls').hide();
          $('.password-reset-ctrls').fadeIn()
              .find('[name=email]').focus();
      }

      function __onSignupLinkClicked(event) {
          event.preventDefault();

          $('.signin-ctrls, .password-reset-ctrls .update-ctrls .get-ugames-ctrls').hide();
          $('.signup-ctrls').fadeIn()
              .find('[name=email]').focus();
      }

      function __onUpdateLinkClicked(event) {
            event.preventDefault();

            $('.signin-ctrls, .password-reset-ctrls .signup-ctrls .get-ugames-ctrls').hide();
            $('.update-ctrls').fadeIn()
              .find('[name=username]').focus();

      }

      function __onLoginButtonClicked(event) {

          event.preventDefault();
          //console.log("vampira");
          //this.$el.modal();
      }

    function submitAsSignUp($form) {
        $('.signup-ctrls .server-message strong').text("");
        data = JSON.stringify({
            'email'    : $form.find("div.signup-ctrls [name=email]").val(),
            'username' : $form.find("div.signup-ctrls [name=username]").val(),
            'password1': $form.find("div.signup-ctrls [name=password1]").val(),
            'password2': $form.find("div.signup-ctrls [name=password2]").val()
        });

        $.ajax({
            url: server_url+'/auth/login',
            type: 'POST',
            contentType: 'application/json',
            data: data,
            xhrFields: {
                withCredentials: true
            },
            //dataType: 'json',
            //headers:{"Origin" : "chrome-extention://mkhojklkhkdaghjjfdnphfphiaiohkef"},
            success: function(data){
                console.log(data);
                console.log("device control succeeded");
                if(String(data).length >= 3){
                __onSignupFailed(data);
                }
                else {
                    $("#username-button").text($form.find("div.signup-ctrls [name=username]").val());
                    $("#auth-form-modal").modal('hide');
                    var u_info_url = server_url + "/user/?username="+$form.find("div.signup-ctrls [name=username]").val();
                    $("#user-info-link").attr("href", u_info_url);
                }
            },
            error: function(data){
                console.log(data);
                console.log("Device control failed");
                __onSignupFailed(data);
            },
            //processData: false,
            // origin : chrome-extention://mkhojklkhkdaghjjfdnphfphiaiohkef
        });
    }


    function __onSignupFailed(errors) {
           var $signupCtrls = $('.signup-ctrls');
           var errorstr = String(errors);

           $('.signup-ctrls .server-message strong').text("");
           $('.signup-ctrls .server-message strong').text(errorstr);

       }

     function submitAsUpdate($form) {
        console.log("inside submit as update");
        //var $form = $(event.currentTarget);



        jsn = JSON.stringify({
          'username' : $form.find("div.update-ctrls [name=username]").val(),
          'gamename': $form.find("div.update-ctrls [name=gamename]").val(),
          'newstate': $form.find("div.update-ctrls [name=newstate]").val()
        });

        $.ajax({
            url: server_url+'/state_update',
            type: 'POST',
            contentType: 'application/json',
            xhrFields: {
                withCredentials: true
            },
            data: jsn,
            //headers:{"Origin" : "chrome-extention://mkhojklkhkdaghjjfdnphfphiaiohkef"},
            success: function(data){
                console.log(data);
                console.log("device control succeeded");
            },
            error: function(){
            //console.log(data);
                console.log("Device control failed");
            },
        //processData: false,
        // origin : chrome-extention://mkhojklkhkdaghjjfdnphfphiaiohkef
        /*
         xhrFields: {
                withCredentials: true
            },
            crossDomain: true
        */
        });
      }

      function submitAsReset($form) {
        jsn = JSON.stringify({'email': $form.find('div.password-reset-ctrls [name=email]').val()});

        $.ajax({
            url: server_url+'/auth/openid_reset',
            type: 'POST',
            contentType: 'application/json',
            data: jsn,
            //headers:{"Origin" : "chrome-extention://mkhojklkhkdaghjjfdnphfphiaiohkef"},
            success: function(data){
                console.log(data);
                console.log("device control succeeded");
            },
            error: function(){
                console.log("Device control failed");
            },
        //processData: false,
        // origin : chrome-extention://mkhojklkhkdaghjjfdnphfphiaiohkef
        });
        /*
          this.model.resetPassword({
              'email': $form.find('div.password-reset-ctrls [name=email]').val()
          });
        */
      }

    function submitAsSignIn($form) {
        //console.log($form);
        //console.log($form.find("div.signin-ctrls [name=username]").val());
        data = JSON.stringify({
          'username': $form.find("div.signin-ctrls [name=username]").val(),
          'password': $form.find("div.signin-ctrls [name=password]").val()
        });

        //console.log(data)
        $.ajax({
            url: server_url+'/auth/login',
            type: 'POST',
            contentType: 'application/json',
            xhrFields: {
                withCredentials: true
            },
            data: data,
            //headers:{"Origin" : "chrome-extention://mkhojklkhkdaghjjfdnphfphiaiohkef"},
            success: function(data){
                console.log(data);
                console.log("device control succeeded");
                if(String(data).length >= 15){
                __onSignupFailed(data);
                }
                else {
                    $("#username-button").text($form.find("div.signin-ctrls [name=username]").val());
                    $("#auth-form-modal").modal('hide');
                    var u_info_url = server_url + "/user/?username="+$form.find("div.signin-ctrls [name=username]").val();
                    $("#user-info-link").attr("href", u_info_url);
                }
            },
            error: function(){
                console.log("Device control failed");
            },

            /*
            xhrFields: {
                withCredentials: true
            },
            crossDomain: true
            */
        //processData: false,
        // origin : chrome-extention://mkhojklkhkdaghjjfdnphfphiaiohkef
        });

       // url: 'http://sgtest.bergur.biz/auth/login',
      //$.post('http://sgtest.bergur.biz/auth/login',jsn,function(data,status){console.log("Data: " + data + " \nStatus: " + status)});
      //$.post('http://localhost:12315/auth/login',jsn,function(data,status){console.log("Data: " + data + " \nStatus: " + status)});
      //$.postJSON('http://localhost:12315/auth/login',jsn,function(data,status){console.log("Data: " + data + " \nStatus: " + status)});

      }





      /*
      __onModalHidden: function(event) {
        console.log("__onModalHidden");
        this.__onLoginLinkClicked(event);
      },

      __onLoginButtonClicked: function(event) {

          event.preventDefault();
          console.log("vampira");
          this.$el.modal();
      },

      __onLogoutButtonClicked: function(event) {
          event.preventDefault();
          this.model.logoutUser();
      },



      __onSignupLinkClicked: function(event) {
          event.preventDefault();

          this.$('.signin-ctrls, .password-reset-ctrls').hide();
          this.$('.signup-ctrls').fadeIn()
              .find('[name=email]').focus();
      },

      __onLoginLinkClicked: function(event) {
          event.preventDefault();

          this.$('.signup-ctrls, .password-reset-ctrls').hide();
          this.$('.signin-ctrls').fadeIn()
              .find('[name=username]').focus();
      },

      __onPasswordResetLinkClicked: function(event) {
          event.preventDefault();

          this.$('.signin-ctrls, .signup-ctrls').hide();
          this.$('.password-reset-ctrls').fadeIn()
              .find('[name=email]').focus();
      },

      __onFormSubmitted: function(event) {
          event.preventDefault();

          var $source = $(event.currentTarget);

          if (this.$signinBtn.is(':visible'))
              this.submitAsSignIn($source);
          else if (this.$signupBtn.is(':visible'))
              this.submitAsSignUp($source);
          else {
              $('#password-reset-loader').show();
              this.submitAsReset($source);
          }
      },

      __onResetSent: function(message) {
          this.$('.password-reset-ctrls .server-message strong').text(message);
      },

      __onLoginFailed: function(errors) {
         var property;

         // Notify user of login errors
         property = 'errant_fields';
         if (property in errors)
             this.$('.signin-ctrls .server-message strong').text(errors[property]["err"]);
       },

       __onSignupFailed: function(errors) {
           var $signupCtrls = this.$('.signup-ctrls');
           var errorProp    = 'errant_fields';

           // Clear error messages first
           $signupCtrls.find('.control-group').removeClass('error');

           if (errorProp in errors)
               _.each(errors[errorProp], function(message, field) {
                   $signupCtrls.find('input[name=' + field + ']')
                       .siblings('.help-block')
                           .text(message)
                           .end()
                       .closest('.control-group')
                           .addClass('error');
               }, this);
       }

       */