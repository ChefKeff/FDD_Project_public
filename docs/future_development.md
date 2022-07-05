# 🔨 Developing ☀️Solveig☀️ further 🔨

In order to improve Solveig further there are some things that can be further developed. Here are some of my suggestions:

1. Using an actual mail-service for the alert subscription system - alternatively using ProptechOS to send alerts. For mailing system I think that <a href="https://sendgrid.com/">SendGrid</a> looks quite good. It is the same mailing system that ProptechOS uses for their alerts (as far as I've understood at least). The API looks quite easy to use and using a mailing system would be more secure than doing the current SMTP-solution that I have implemented.
2. Using a database (like <a href="https://mongodb.com">Mongo DB</a>) to store the emails that are supposed to receive alerts is also better than storing that information locally in a ```.csv```-file.
3. Using a database for storing the API-keys and other secrets.
4. Using service objects in ProptechOS instead of emails. I will probably spend some time trying to understand integrating it this summer.

### Deep diving into the effect of different parameters on the machine learning model

Spending some time understanding how much irradiance, temperature, humidity and other parameters *actually* impact the precision of the machine learning model is quite important in order to create good and meaningful models. Also, writing the algorithm in such a way that it handles missing values in a good way is pertinent in making a good model.

## Why have I not implemented this?

Since the version of Solveig that I have made is more of a pilot or a <a href="https://en.wikipedia.org/wiki/Proof_of_concept">Proof of concept</a> I feel like using paid services is quite unnecessary. Since the goal of the application is just to show people *how* the PV data could be used, putting a lot of work and money into the scalability of the app might not be top priority.
