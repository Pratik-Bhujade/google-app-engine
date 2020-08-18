# Google App Engine Repository


## Prerequisites
1. A Google Cloud Platform Account
2. [A new Google Cloud Platform Project][7] for this lab with billing optional if not using at large scale
 (You can choose the region for App Engine deployment with advanced options.)
3. Enable the Cloud Vision API and Cloud Translation API from
 [the API Manager][8]

[7]: https://console.developers.google.com/project
[8]: https://console.developers.google.com

## Deploy the application

```shell
$ gcloud app create
$ gcloud datastore indexes create index.yaml
$ gcloud app deploy
```

By executing these commands on the Cloud Shell, the project id is automatically
 applied to the application and the application URL will be
 https://\<project id\>.appspot.com.

You can see Datastore's index creation status from the Cloud Console. Once
 indexes have been created successfully, you can start using the application.

## Clean up
Clean up is really easy, but also super important: if you don't follow these
 instructions, you will continue to be billed for the project you created.

To clean up, navigate to the [Google Developers Console Project List][12],
 choose the project you created for this lab, and delete it. That's it.

[12]: https://console.developers.google.com/project
