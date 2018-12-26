import os
from flask import Flask, request, abort
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
    FlexSendMessage,
    BubbleContainer,
    ButtonComponent,
    BoxComponent,
    ImageComponent,
    TextComponent,
    IconComponent,
    SeparatorComponent,
    SpacerComponent,
    URIAction

)
from future_chip import FutureChipReport, Figure, GetFutureRealtime

app = Flask(__name__)

linet = os.getenv('linet')
lines = os.getenv('lines')

line_bot_api = LineBotApi(linet)
handler = WebhookHandler(lines)


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/test')
def test_page():
    return 'In test page!'


@app.route('/plotly.html')
def plotly():
    date = request.args.get('date', '', type=str)
    if date == '':
        return figure
    else:
        figured = figure_html(date)
        return figured


@app.route('/future_option')
def future_option():
    date = request.args.get('date', '', type=str)
    if date == '':
        return table
    else:
        tabled = table_html(date)
        return tabled


@app.route('/future_realtime')
def realtime():
    x = GetFutureRealtime()
    return x.realtime_output()[0]


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


def table_html(date):
    x = FutureChipReport(date)
    table = x.add_html()
    return table


def figure_html(date):
    x = Figure(date, "5Min")
    x.add_macd()
    x.add_dif_change()
    x.writer('templates', filename='plotly')
    with open('templates/plotly.html', 'r') as f:
        figure = f.read()
        f.close()
    return figure


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text == 'now':
        text = realtime()
    elif event.message.text == 'hi':
        bubble = BubbleContainer(
            direction='ltr',
            hero=ImageComponent(
                url='https://img.icons8.com/metro/1600/search.png',
                size='full',
                aspect_ratio='20:13',
                aspect_mode='cover',
                action=URIAction(uri='http://example.com', label='label')
            ),
            body=BoxComponent(
                layout='vertical',
                contents=[
                    # title
                    TextComponent(text='Brown Cafe', weight='bold', size='xl'),
                    # review
                    BoxComponent(
                        layout='baseline',
                        margin='md',
                        contents=[
                            IconComponent(size='sm', url='https://img.icons8.com/metro/1600/search.png'),
                            IconComponent(size='sm', url='https://img.icons8.com/metro/1600/search.png'),
                            IconComponent(size='sm', url='https://img.icons8.com/metro/1600/search.png'),
                            IconComponent(size='sm', url='https://img.icons8.com/metro/1600/search.png'),
                            IconComponent(size='sm', url='https://img.icons8.com/metro/1600/search.png'),
                            TextComponent(text='4.0', size='sm', color='#999999', margin='md',
                                          flex=0)
                        ]
                    ),
                    # info
                    BoxComponent(
                        layout='vertical',
                        margin='lg',
                        spacing='sm',
                        contents=[
                            BoxComponent(
                                layout='baseline',
                                spacing='sm',
                                contents=[
                                    TextComponent(
                                        text='Place',
                                        color='#aaaaaa',
                                        size='sm',
                                        flex=1
                                    ),
                                    TextComponent(
                                        text='Shinjuku, Tokyo',
                                        wrap=True,
                                        color='#666666',
                                        size='sm',
                                        flex=5
                                    )
                                ],
                            ),
                            BoxComponent(
                                layout='baseline',
                                spacing='sm',
                                contents=[
                                    TextComponent(
                                        text='Time',
                                        color='#aaaaaa',
                                        size='sm',
                                        flex=1
                                    ),
                                    TextComponent(
                                        text="10:00 - 23:00",
                                        wrap=True,
                                        color='#666666',
                                        size='sm',
                                        flex=5,
                                    ),
                                ],
                            ),
                        ],
                    )
                ],
            ),
            footer=BoxComponent(
                layout='vertical',
                spacing='sm',
                contents=[
                    # callAction, separator, websiteAction
                    SpacerComponent(size='sm'),
                    # callAction
                    ButtonComponent(
                        style='link',
                        height='sm',
                        action=URIAction(label='CALL', uri='tel:000000'),
                    ),
                    # separator
                    SeparatorComponent(),
                    # websiteAction
                    ButtonComponent(
                        style='link',
                        height='sm',
                        action=URIAction(label='WEBSITE', uri="https://example.com")
                    )
                ]
            ),
        )
        message = FlexSendMessage(alt_text="hello", contents=bubble)
        line_bot_api.reply_message(
            event.reply_token,
            message
        )
    elif event.message.text == '1':
        bubble = {
                    "type": "bubble",
                    "header": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                        {
                            "type": "text",
                            "text": "Header text"
                        }
                        ]
                    },
                    "hero": {
                        "type": "image",
                        "url": "https://example.com/flex/images/image.jpg"
                    },
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                        {
                            "type": "text",
                            "text": "Body text"
                        }
                        ]
                    },
                    "footer": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                        {
                            "type": "text",
                            "text": "Footer text"
                        }
                        ]
                    },
                    "styles": {
                        "comment": "See the example of a bubble style object"
                    }
                }
        message = FlexSendMessage(alt_text="one", contents=bubble)
        line_bot_api.reply_message(
            event.reply_token,
            message
        )
    else:
        try:
            global table
            table = table_html(event.message.text)
            global figure
            figure = figure_html(event.message.text)
            text = 'table- line://app/1625409055-qZAO6DX0, figure- line://app/1625409055-N5KnD0yY'
        except:
            text = event.message.text
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=text))


if __name__ == "__main__":
    app.run()