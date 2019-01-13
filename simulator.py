from datetime import datetime
import os
from flask import Flask, request
from flask_restful import Resource, Api, reqparse

app = Flask(__name__)
collection = None

account = os.getenv('account')


@app.route("/face_detect.html")
def face_detect():
    """
    A demo page for face_detect.
    """
    return """
<form action="api/face_detect" method="post" enctype="multipart/form-data">
    Select image to upload:
    <input type="file" name="image" id="image">
    <input type="submit" value="Upload Image" name="submit">
</form>
    """


class Record(Resource):
    def get(self):
        operation = request.args.get('operation', 'cover', type=str)
        point = request.args.get('point', type=str)
        date = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        profit = '-'
        if operation == 'cover':
            myvar = open(account, 'r')
            lst = myvar.readlines()
            buysell = lst[-1].split(',')[1]
            last = int(lst[-1].split(',')[2])
            if buysell == 'buy':
                profit = str(int(point) - last)
            else:
                profit = str(last - int(point))

        with open(account, 'a') as fd:
            fd.write('\n')
            fd.write('{},{},{},{},{}'.format(date, operation, point, '-',
                                             'order'))
            fd.write('\n')
            date = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            fd.write('{},{},{},{},{}'.format(date, operation, point, profit,
                                             'deal'))
            fd.close()
        os.system('bash $simulator')
        return 'ok'


if __name__ == "__main__":
    api = Api(app)
    api.add_resource(Record, '/api/record')
    app.run(host="0.0.0.0")