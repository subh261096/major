 $(document).ready(function () {
        $('#success').click(function (e) {
          e.preventDefault()
         $('#message').html('<div class="alert alert-success fade in"><button type="button" class="close close-alert" data-dismiss="alert" aria-hidden="true">×</button>This is a success message</div>');
           })
        }