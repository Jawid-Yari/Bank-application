
var start_index = 20;

$('#load-more').click(function() {
    var account_id = $(this).data('account-id');
    $.getJSON('/account-history/'+ account_id + '/transactions', { start_index: start_index }, function(data) {
        if (data.transactions.length > 0) {
            $.each(data.transactions, function(_index, transaction) {
                var transaction_html = '<tr><td>' + transaction.Id + '</td><td>' + transaction.AccountId + '</td><td>' + transaction.Date + '</td></tr>' + transaction.Operation + '</td></tr>' + transaction.Amount + '</td></tr>';
                $('#transactions-table tbody').append(transaction_html);
            });
            start_index += 20;
        } else {
            $('#load-more').hide();
        }
    });
});