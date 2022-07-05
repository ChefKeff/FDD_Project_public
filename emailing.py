import yagmail


def send_sub_conf(email, user, app_password):
    """
    Sends an email confirming that a person has subscribed
    """
    subject = 'Prenumerationsbekräftelse - Solveig'
    content = ['''<h1>Hej kompis!</h1>
    <p>Du prenumererar nu på larm från Solveig - kul! ☀️ </p>
    <p><strong>Har det blivit något fel?</strong> Du kan avregistrera dig från avvikelserapporteran <a href="http://127.0.0.1:5000/unsub>här</a>.</p>
    <p>Vid några frågor, var god kontakta Niklas Norinder på Niklas.Norinder@vasakronan.se eller norinderniklas@gmail.com</p>
    <h3>Ha en fin dag! <br> Allt gott, <br> Solveig</h3>''']

    with yagmail.SMTP(user, app_password) as yag:
        yag.send(email, subject, content)
        print('Sent email successfully')


def send_remove_conf(email, user, app_password):
    """
    Sends an email confirming that a person has unsubscribed
    """
    subject = 'Avprenumerationsbekräftelse - Solveig'
    content = ['''<h1>Hej kompis!</h1>
    <p>Du prenumererar nu inte längre på larm från Solveig - tråkigt att du lämnar. 🌙</p>
    <p>Vid några frågor, var god kontakta Niklas Norinder på Niklas.Norinder@vasakronan.se eller norinderniklas@gmail.com</p>
    <h3>Ha en fin dag! <br> Allt gott, <br> Solveig</h3>''']

    with yagmail.SMTP(user, app_password) as yag:
        yag.send(email, subject, content)
        print('Sent email successfully')


def send_alert(email, name, city, id, frm, to, user, app_password):
    """
    Sends an email alerting that the production of some solar panel differs too much (!!!)
    """

    subject = f'Larm för {name} - Solveig'
    content = [
        f'''<h1>Hej!</h1>
        <p>Det verkar vara nåt tokigt med en av solcellsanläggningarna som du prenumererar på. Den producerade elen har skiljt sig mer än 50% från den förväntade elproduktionen 6 dagar i följd. 
        <br>Den påverkade anläggningen är {name}. För att undersöka det närmre kan du kolla i <a href="http://127.0.0.1:5000/selected?PV-start={frm}&PV-end={to}&city={city}&meters={id}">Solveig</a>.</p>
        <p>Vid några frågor kring detta mail, var god kontakta Niklas Norinder på Niklas.Norinder@vasakronan.se eller norinderniklas@gmail.com</p>
        <h3>Ha en fin dag & hoppas inte det är nåt allvarligt! <br> Allt gott, <br> Solveig</h3>''']

    with yagmail.SMTP(user, app_password) as yag:
        yag.send(email, subject, content)
        print('Sent email successfully')
