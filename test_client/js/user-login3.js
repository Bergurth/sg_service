

     $("#login-button").click(_.bind(__onLoginLinkClicked));
     $('.signup-ctrls').hide();
     $('.password-reset-ctrls').hide();

     $("#signup-link").click(_.bind(__onSignupLinkClicked));

     $signupBtn = $("#signup-submit");
     $signinBtn = $("#signin-submit");

     $(".auth-form").submit(_.bind(this.__onFormSubmitted, this));
     $(".btn-login").click(_.bind(__onLoginButtonClicked));

     function __onLoginLinkClicked(event) {
          console.log("__onModalShown")
          $('div.signin-ctrls [name=username]').focus();
      }

      function __onFormSubmitted(event) {
          event.preventDefault();

          var $source = $(event.currentTarget);

          if ($signinBtn.is(':visible'))
              submitAsSignIn($source);
          else if ($signupBtn.is(':visible'))
              this.submitAsSignUp($source);
          else {
              $('#password-reset-loader').show();
              submitAsReset($source);
          }
      }

      function __onSignupLinkClicked(event) {
          event.preventDefault();

          $('.signin-ctrls, .password-reset-ctrls').hide();
          $('.signup-ctrls').fadeIn()
              .find('[name=email]').focus();
      }

      function __onLoginButtonClicked(event) {

          event.preventDefault();
          console.log("vampira");
          this.$el.modal();
      }

      function submitAsSignUp($form) {
          jsn = JSON.stringify({
              'email'    : $form.find("div.signup-ctrls [name=email]").val(),
              'username' : $form.find("div.signup-ctrls [name=username]").val(),
              'password1': $form.find("div.signup-ctrls [name=password1]").val(),
              'password2': $form.find("div.signup-ctrls [name=password2]").val()
          });
          $.ajax({
          type: 'POST',
          contentType: 'application/json',
          data: jsn,
          dataType: 'json',
          //headers:{"Origin" : "chrome-extention://mkhojklkhkdaghjjfdnphfphiaiohkef"},
          success: function(data){
          console.log("device control succeeded");
          },
        error: function(){
        console.log("Device control failed");
        },
        //processData: false,
        // origin : chrome-extention://mkhojklkhkdaghjjfdnphfphiaiohkef
        url: 'http://localhost:12315/auth/login'
        });
      }

        function submitAsSignIn($form) {
          console.log($form);
          console.log($form.find("div.signin-ctrls [name=username]").val());
          jsn = JSON.stringify({
              'username': $form.find("div.signin-ctrls [name=username]").val(),
              'password': $form.find("div.signin-ctrls [name=password]").val()
          });
          // make ajax call
          /*
          $.ajax({
          type: 'POST',
          contentType: 'application/json',
          data: jsn,
          dataType: 'json',
          success: function(data){
          console.log("device control succeeded");
          },
        error: function(){
        console.log("Device control failed");
        },
        //processData: false,

        url: 'http://sgtest.bergur.biz/auth/login'
        });
    */
        console.log(jsn)
        $.ajax({
          type: 'POST',
          contentType: 'application/json',
          data: jsn,
          dataType: 'json',
          //headers:{"Origin" : "chrome-extention://mkhojklkhkdaghjjfdnphfphiaiohkef"},
          success: function(data){
          console.log("device control succeeded");
          },
        error: function(){
        console.log("Device control failed");
        },
        //processData: false,
        // origin : chrome-extention://mkhojklkhkdaghjjfdnphfphiaiohkef
        url: 'http://localhost:12315/auth/login'
        });
    /*
    $.ajax({
  type: 'POST',
  url: 'http://sgtest.bergur.biz/auth/login',
  data: jsn,
  error: function(e) {
    console.log(e);
  },
  dataType: "json",
  contentType: "application/json"
});
*/

      //$.post('http://sgtest.bergur.biz/auth/login',jsn,function(data,status){console.log("Data: " + data + " \nStatus: " + status)});
      //$.post('http://localhost:12315/auth/login',jsn,function(data,status){console.log("Data: " + data + " \nStatus: " + status)});
      //$.postJSON('http://localhost:12315/auth/login',jsn,function(data,status){console.log("Data: " + data + " \nStatus: " + status)});
          /*
          this.model.loginUser({
              'username': $form.find("div.signin-ctrls [name=username]").val(),
              'password': $form.find("div.signin-ctrls [name=password]").val()
          });
     */
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