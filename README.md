# Welcome Home

Positive customer experience in onboarding reflects on your brand and can drive high value referral from a customer's closest network. So when a new customer signs up it is important that you put your best foot forward to welcome them. In this demo we show how you can use [MailChimp](https://mailchimp.com/), a best-in-class marketing automation tool, to drive your welcome pack experience. This opens up potential for sending people on different welcome journeys depending on how they came to be a customer, A/B testing options to drive further engagement, and all of the great features you expect from marketing automation.

![Sample Email](sample-email.png)

In this demo we connect the Gentrack Platform to an integration layer, represented by Heroku. This layer extracts a bit of extra data that might typically reside in a CRM, and sends the combined set to Mailchimp to trigger the automation pathway. The process flows as follows:

![Flow](flow.png)

1. Deploy an integration to orchestrate the customer welcome message workflow
2. Subscribe to event(s) via the Gentrack Platform Developer Portal to be received by your integration layer
3. Gentrack Platform picks up the event and packages it up to send to your integration layer via a webhook
4. Your integration layer enriches the event with other information from around your organization then sends it to the marketing automation tool
5. Your marketing automation tool initiates the welcome pack communications journey

As you think about your production deployment you might choose other methods for integration (e.g. event bus, workflow-based integration layer, etc...). Our sample integration layer also hosts a simple data set that might be obtained from a customer relationship management (CRM) system. You will also want to consider how to secure secrets, such as API keys, in your integration layer.

## Before you begin

You will need to have:

* [Gentrack Platform Developer Portal](https://portal.gentrack.io) Account - contact your organization administrator to get an invite, or your account manager to enroll your organization
* [MailChimp](https://mailchimp.com/) Account
* [Heroku](https://www.heroku.com/) Account

## Obtain MailChimp API key and Gentrack Platform app public key

Before you deploy the integration you will need an API key for MailChimp to pre-configure and push events to its API. You will also need the public key of your Gentrack Platform app definition to verify that received events are valid.

1. Sign in to [MailChimp](https://admin.mailchimp.com/)
2. Navigate to your account, locate the [API keys](https://admin.mailchimp.com/account/api/) in the Extras section, and generate a new API key - save it for later
3. Sign in to the [Gentrack Platform Developer Portal](https://portal.gentrack.io/)
4. Add a new app using your non-production tenant
5. Open the app settings and copy the public key - save it for later

## Deploy the sample integration on Heroku

It is time to deploy the integration. This will setup an app in Heroku to connect MailChimp and Gentrack Platform, and create a new MailChimp list to receive new customers.

1. Click the **Deploy to Heroku** button to create a new instance of this sample integration:

    [![Deploy to Heroku](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy?template=https://github.com/Gentrack/gcis-demo-welcome-home)
2. On the __Create New App__ populate the following values then click **Deploy app**
    * App name - provide a value, or leave it blank to let Heroku generate a value
    * Region - chooses a region that suits you
    * MAILCHIMP_API_KEY - paste the MailChimp API key you obtained earlier
    * MAILCHIMP_LIST_NAME - provide a name for a new list in MailChimp which we will create for the integration (e.g. "Energise Me"), be aware this is also used as the organization name in the starter email template.
    * APP_PUB_KEY - paste the Platform public key you obtained earlier

Once the application is deployed you will be able to access the integration console at `https://(your-app-name).herokuapp.com/admin`.

## Configure the MailChimp campaign

Now that the integration is setup, it is time to wire up an automated campaign which is triggered with each new entry to a list. We will use a pre-created "Welcome Pack" email template which has the merge fields pre-populated:

1. [Click to import our starter "Welcome Pack" email template](https://admin.mailchimp.com/templates/share?id=90164641_cdfd77dd092f71ce6ef6_us17)
2. Create a new campaign using the **Welcome new subscribers** blueprint using the list you specified during the integration setup
3. Once the campaign is created, in the setup wizard click **Edit trigger**
4. On the __Edit trigger__ page set **Delay** to **immediately**, then click **Update Trigger** to return to the setup wizard
5. On the setup wizard, click **Edit Workflow Settings**
6. On the __Workflow configuration__ page set the **From name** and **From email address** to a valid value then click **Update settings**
7. On the setup wizard, step click **Design Email**
8. On the __Email information__ page click **Next**
9. On the __Select a template__ page under __Saved templates__ select the **Welcome Pack** template
10. On the message design screen review the design, then click **Save and Continue** to return to the setup wizard
11. At the bottom of the setup wizard, click **Next**
12. On the __Review your workflow__ page ensure there are no issues, then click **Start Workflow**

**NOTE**: To preserve the drag-and-drop capability of email templates, you need to import templates using the share template functionality. MailChimp has an HTML import API but it appears to disable the use of the visual editor at the time of this writing.

## Add a sample user to the integration layer CRM dataset

As we are simulating an external dataset that might come from a CRM you will need to add a record that will match with the test event you will send:

1. Sign in to the integration console (you can find it at `https://(your-app-name).herokuapp.com/admin`) using the username `admin` and password `integrations-are-fun!`.
2. In the __Welcome Pack Orchestration__ section click **Add** next to **Customers**
3. On the __Add customer__ page provide then click **Save**:
    * Account ID - provide a value that you will use in the test event (e.g. 12345678)
    * First Name - provide a value that will be used as the customer's first name
    * Last Name - provide a value that will be used as the customer's last name
    * Email Address - provide a value that will receive the email

You can add as many entires as needed.

## Subscribe to the welcome event and send a test event

Now that the integration layer and MailChimp are configured, it is time to connect the app you created earlier in the Gentrack Platform Developer Portal to the integration layer and send a test event:

1. Sign in to the [Gentrack Platform Developer Portal](https://portal.gentrack.io/)
2. Open the app settings for the app you created earlier
3. Under __App Settings__ click **Event Subscriptions**
4. On the __Event Subscriptions__ page click **Edit**
5. In the __Edit Events__ dialog provide the following then click **Save**:
    * URL of your End Point: `https://(your-app-name).herokuapp.com/webhook/`
    * Select the **customer-welcome** event
6. Once the event is subscribed, click the **Send Test Event** button
7. In the __Send Test Event__ dialog set the Account ID to the value you setup in the integration console earlier, then click **Send**

In a few moments you should receive your sample welcome pack!

## Cleaning up your resources

Make sure to clean up after you are done experimenting with the sample, otherwise you may incur unexpected costs associated with each of the services:

* In MailChimp you can delete the campaign, list, and template
* In Heroku you can delete the application
* In Gentrack Platform you can delete the application
