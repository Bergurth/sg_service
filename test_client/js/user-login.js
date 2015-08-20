(function($){
   var UserLogin = Menntagatt.Utils.namespace('Menntagatt.App.UserLogin');
   
   UserLogin.View = Backbone.View.extend({
      $templates: null,
      $signupBtn: $(),
      $signinBtn: $(),
      
      initialize: function() {
         this.$('.signup-ctrls').hide();
         this.$('.password-reset-ctrls').hide();
         this.$signupBtn = this.$("#signup-submit");
         this.$signinBtn = this.$("#signin-submit");
         
         this.$("#signup-link").click(_.bind(this.__onSignupLinkClicked, this));
         this.$("#signin-link").click(_.bind(this.__onLoginLinkClicked, this));
         this.$('#cancel-reset-link').click(_.bind(this.__onLoginLinkClicked, this));
         this.$('#password-reset-link').click(_.bind(this.__onPasswordResetLinkClicked, this));
         
         this.$(".auth-form").submit(_.bind(this.__onFormSubmitted, this));
         
         $(".btn-login").click(_.bind(this.__onLoginButtonClicked, this));
         $(".btn-logout").click(_.bind(this.__onLogoutButtonClicked, this));
         
         this.$el
             .on('shown.bs.modal', _.bind(this.__onModalShown, this))
             .on('hidden.bs.modal', _.bind(this.__onModalHidden, this));
         
         this.model
             .on('evt:reset-request-sent', this.__onResetSent, this)
             .on('evt:login-failed', this.__onLoginFailed, this)
             .on('evt:signup-failed', this.__onSignupFailed, this);
      },
      
      submitAsSignUp: function($form) {
          this.model.signupUser({
              'email'    : $form.find("div.signup-ctrls [name=email]").val(),
              'username' : $form.find("div.signup-ctrls [name=username]").val(),
              'password1': $form.find("div.signup-ctrls [name=password1]").val(),
              'password2': $form.find("div.signup-ctrls [name=password2]").val()
          });
      },
 
      submitAsSignIn: function($form) {
          this.model.loginUser({
              'username': $form.find("div.signin-ctrls [name=username]").val(),
              'password': $form.find("div.signin-ctrls [name=password]").val()
          });
      },
      
      submitAsReset: function($form) {
          this.model.resetPassword({
              'email': $form.find('div.password-reset-ctrls [name=email]').val()
          });
      },
      
      __onModalShown: function(event) {
          this.$('div.signin-ctrls [name=username]').focus();
      },
      
      __onModalHidden: function(event) {
          this.__onLoginLinkClicked(event);
      },
      
      __onLoginButtonClicked: function(event) {
          event.preventDefault();
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
    });
   
   UserLogin.Model = Backbone.Model.extend({
      user: null,
      
      initialize: function() {
         this.user = new Menntagatt.Models.User();
      },
      
      signupUser: function(signupData) {         
         this.user.save(signupData, {
            url: '/openid_login/json',
            
            success: _.bind(function (model, response) {
               window.location = window.location.href;
            }, this),
                  
            error: _.bind(function (model, jqXHR) {
               var errors = JSON.parse(jqXHR.responseText);
               
               this.trigger('evt:signup-failed', errors);
            }, this)
         });
      },
      
      loginUser: function(loginData) {         
         this.user.save(loginData, {
            url: '/openid_login/json',
            
            success: _.bind(function (model, response) {
               window.location = window.location.href;
            }, this),
                  
            error: _.bind(function (model, jqXHR) {
               var errors = JSON.parse(jqXHR.responseText);
               
               this.trigger('evt:login-failed', errors);
            }, this)
         });
      },
      
      logoutUser: function() {
         this.user.fetch({
            url: '/openid_logout/json',
            success: _.bind(function (model, response) {
               window.location = "/";
            }, this)
         });
      },
      
      resetPassword: function(data) {
          $.ajax({
              url : '/openid_reset/json',
              type: 'post',
              data: JSON.stringify(data),
              
              contentType: 'application/json',
              dataType   : 'json',
              
              success: function(response) {
                  this.trigger('evt:reset-request-sent', response);
                  $('#password-reset-loader').hide();
              },
              
              context: this
          });
      }
   });
})(jQuery);
