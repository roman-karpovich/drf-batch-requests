=====================
DRF batch requests
=====================

Quick start
-----------


ideal:

var facebook_batch_requests = [
    {method: 'GET', relative_url: '/me?fields=birthday,name,email,gender,age_range,first_name,last_name&locale=en_US'},
    {method: 'GET', relative_url: '/me/taggable_friends?fields=name,first_name,last_name,picture.width(400).height(400)&limit=1000&locale=en_US'},
    {method: 'GET', relative_url: '/me/albums?fields=type,name&locale=en_US&limit=100', name: 'albums', omit_response_on_success:true},
    {method: 'GET', relative_url: '/photos?ids={result=albums:$.data.*.id}&fields=source,created_time,likes{name},tags{name},album{type,name},comments{from,message,created_time,likes{name},message_tags}&locale=en_US&limit=1000'},
    {method: 'GET', relative_url: '/me/feed?fields=from,type,message,description,updated_time,likes{name},message_tags,comments{from,message,created_time,likes{name},message_tags}&limit=100&locale=en_US'}
];
