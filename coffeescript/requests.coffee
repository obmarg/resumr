define(
  [ ],
  ( ) ->
    InitRequests = ->
      amplify.request.define( 'SelectHistoryItem', 'ajax',
        url: '/api/sections/{name}/history/select/{id}'
        type: 'POST'
      )

    return InitRequests
)
