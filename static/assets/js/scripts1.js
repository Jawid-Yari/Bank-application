$(document).ready(function() {
    var offset = 20;
    var limit = 20;
    var account_id =  (account.Id)
  
    $('#load-more').click(function() {
      $.get('/account-history/' + account_id + '/transactions', {offset: offset, limit: limit}, function(data) {
        if (data.transactions.length > 0) {
          var table = $('#transaction-table');
          $.each(data.transactions, function(i, transaction) {
            table.append('<tr><td>' + transaction.Date + '</td><td>' + transaction.Amount + '</td><td>' + transaction.Type + '</td></tr>');
          });
          offset += limit;
        }
        if (data.transactions.length < limit) {
          $('#load-more').hide();
        }
      });
    });
  });