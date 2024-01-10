from pymongo import MongoClient 
import numpy as np
import os
from bson import ObjectId
from datetime import datetime
from flask import Flask, jsonify,request
from bson.json_util import dumps
#er

app = Flask(__name__)

# Your connection details
connection_string = r'mongodb://aromongo:%40r0dek%40412@mongodb.arodek.com:27017/?authMechanism=DEFAULT'
database_name = r'Cogniquest'
#users_collection = r'users'

#Naming Test(Q3)
def naming_test(answer_new):
    value = [string.lower() for string in answer_new]
    list_1=[]
    list_2=[]
    list_3=[]
    j = 0
    result_dict={}
    text = ["lion", "camel", ["rhinoceros", "rhino"]]
 
    for index, i in enumerate(value):
        if isinstance(text[index], list):
            if i in text[index]:
                list_1.append(i)
                list_2.append(index)
            else:
                list_3.append("not in list")
        else:
            if i == text[index]:
                list_1.append(i)
                list_2.append(index)
            else:
                list_3.append("not in list")
    try:
        for i in range(len(list_2)):
            result_dict[list_2[i]] = list_1[i]
        for i in result_dict.keys():
            if isinstance(text[i], list):  
                if value[i] in text[i]:
                    j += 1
            elif value[i] == text[i]:
                j += 1
        accuracy3 = j/len(value)
        return accuracy3
    except TypeError:
        return 0 

#Attention Test(Q4)
def attention_test(answer_new):
    value = [answer_new[key] for key in answer_new]
    j=0
    text=['2159836','253407']
    for i,(val, txt) in enumerate(zip(value, text)):
        if val == txt:
            j += 1
    accuracy4=j/len(value)
    return accuracy4

#Language Test(Q5)
def language_test(answer_new):
    value_answer=answer_new.split(',' ' ')
    value = [word.lower() for word in value_answer]
    text = ["clock","chair","computer","cap","cat","candy","cotton","cloud","captain","camera","coal","cucumber","cottage","chalk","car","curd","cart","cow","card","colour","cabin","cabinet","cover","cock","cake","cashew","chocolate","comb","candle","crocodile","cross","christmas"]
    common_words = set(value) & set(text)
    if len(common_words)>=11:
        accuracy5=1
    else:
        accuracy5=0
    return accuracy5

#Abstraction Test(Q6)
def abstraction_test(answer_new):
    j=0
    value = answer_new.lower()
    new_value=[letter.replace(" " ,"_") for letter in value]
    my_lst_str = ''.join(map(str, new_value))
    text = ["vehicle","vehicle_","used_for_transportation","transport_","transport_vehicle"]

    if my_lst_str in [item for item in text]:
        j +=1
    else:
        j=j

    if j==1:
        accuracy6=1
    else:
        accuracy6=0
    return accuracy6

#Delayed Recall Test(Q7)
def delayed_recall_test(answer_new):
    value=[string.lower() for string in answer_new]
    list_1=[]
    list_2=[]
    list_3=[]
    j = 0
    result_dict={}
    text=["banana", "milk", "deer"]
    for index,i in enumerate(value):
        if i in text:
            list_1.append(i)
            list_2.append(index)
        else:
            list_3.append("not in list")
    try:
        for i in range(len(list_2)):
            result_dict[list_2[i]] = list_1[i]
        for i in result_dict.keys():
            if value[i] == text[i] :
                j += 1
        accuracy7 = j/len(value)
        return accuracy7
    except TypeError:
        return 0

def get_result(useid:str,testid:str):
    global connection_string,database_name
    info_dict={'collection_name_3': r'qcollection2',
                'collection_name_4': r'qcollection4',
                'collection_name_5':r'qcollection5',
                'collection_name_6': r'qcollection6',
                'collection_name_7': r'qcollection7',
                'user':r'users',
                'Result':r'Result_Display',
                'userId':useid,
                'testId':testid}
    keys_to_exclude = ['userId', 'user','Result','testId']
    original_accuracy=0
    filtered_values = [value for key, value in info_dict.items() if key not in keys_to_exclude]
    object_id_user=ObjectId(info_dict['userId'])
    object_id=ObjectId(info_dict['testId'])
    client = MongoClient(connection_string)  
    db = client.get_database(database_name)
    age = db[info_dict['user']].find_one({'_id': object_id_user})['age']
    end_time=db[info_dict['collection_name_7']].find_one({"testId": object_id})['testTime']
    #accuracy calculation
    collection_name = [db[collection] for collection in filtered_values]
    for i in collection_name:
        try:
            result_test =i.find_one({'testId':object_id})['testData']
            try:
                accu_1=delayed_recall_test(result_test)
            except:
                accu_1=0
            try:
                accu_2=abstraction_test(result_test)
            except:
                accu_2=0
            try:
                accu_3=language_test(result_test)
            except:
                accu_3=0
            try:
                accu_4=attention_test(result_test)
            except:
                accu_4=0
            try:
                accu_5=naming_test(result_test)
            except:
                accu_5=0
            overall_accuracy=max(accu_1,accu_2,accu_3,accu_4,accu_5)
            original_accuracy=overall_accuracy+original_accuracy
            #test_id =i.find_one({'testId':object_id})['user_id']
            #print(test_id,overall_accuracy,original_accuracy)
        except:
            print("ERROR")
    #speed calculation
    minutes,seconds,nanoseconds=str(end_time).split('.')
    minutes, seconds = int(minutes), int(seconds)

    #test_id_object=ObjectId(test_id)
    speed_user = round(min(100, (((minutes * 60) + seconds) / (6 * 60) * 100)),2)
    overall_accuracy=np.round(original_accuracy*100/5)
    ICA_index=speed_user*overall_accuracy/100
    ##machine_learning
    user_report={ 
    'user_id':useid,
    'test_id':testid,
    'age':age,
    'overall_accuracy':overall_accuracy,
    'overall_speed':speed_user,
    'ICA_index': ICA_index,
    'timestamp':datetime.now().strftime("%Y-%m-%d %H")
    }
    
    db[info_dict['Result']].insert_one(user_report)
    client.close()
    #print(age)
    return dumps(user_report)


@app.route('/result/<string:user_id>/<string:test_id>', methods=['GET'])
def get_result_by_test_id(user_id,test_id):
    list_inputs =[user_id,test_id]
    if user_id and test_id not in list_inputs:
        return jsonify({'error': '404 User not found'})
    else:
        try:
            return get_result(user_id,test_id)
        except TypeError as e:
            return jsonify({"error": 'data_missing'})
        except KeyError :
            return jsonify({"error": 'key_error'})

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))


    
