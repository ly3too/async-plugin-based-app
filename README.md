# A simple asynchronous event loop based publish-subscribe or (pub-sub) implementation

## Channel
used to seperate different message group or 'namespace'

a simple tree structured pub-sub system, a sub channel receives 
all message from the parent channel but not the opposite

use "/" as the root channel, use "/sub_lev1/sub_lev2" to access the sub channel

Callbacks will be put into event loop if interested signal received.

## Dispatch
provide a simple asynchronous pub-sub dispatch mechanism, without channels