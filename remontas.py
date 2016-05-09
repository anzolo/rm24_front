from bottle import route, template, request, abort, static_file, url, redirect
from bson.objectid import ObjectId

import adminka
import common
import conf
import os
import json
import math


# Ремонтас. По маршруту возвращается шаблон
@route('/')
def index():
    return template('remontas')


# Ремонтас. возврат файлов с учетом прав доступа
@route('/remontas/<access>/<filename:path>')
def static(access, filename):
    if access == "public":
        return static_file(filename, root='./remontas/public')
    elif access == "restricted":
        result_check_rights = adminka.check_rights("master", request)
        if result_check_rights["status"]:
            return static_file(filename, root='./remontas/restricted')
        else:
            return abort(401, "Sorry, access denied.")


# API ремонтаса. получение списка мастеров для главной странице по фильтру
@route('/api/main/searchMasters', method='POST')
def rem_doSearchMasters():
    result = dict()

    page = request.json["page"]

    filter = request.json["filter"]
    # разбираем фильтр пришедший от клиента
    query = {'$and': [{'score': {'$gt': 0}}, {'status': 'active'}]}

    if len(filter["kindServices"]) != 0 and len(filter["kindServices"]) != kindServicesCount(filter["category"]):
        for kind_service in filter["kindServices"]:
            query["$and"].append({"categories.kind_services": {'$elemMatch': { "_id":kind_service["_id"], "services":{'$elemMatch':{"price":{"$gt": 0}}}}}})
    elif (filter["category"] is not None) and filter["category"]["_id"] != "all-category":
        # фильтруем только по категории
        query["$and"].append({'categories':{'$elemMatch':{'_id':filter["category"]["_id"],'kind_services': {'$elemMatch': { 'services':{'$elemMatch':{"price":{"$gt": 0}}}}}}}})


    if len(filter["addServices"]) > 0:
        for add_service in filter["addServices"]:
            query["$and"].append({ "additional_service": { '$elemMatch': { '$in': [add_service] } } })

    # if filter["category"] is None or filter["category"]["_id"]=="all-category":
    #     if len(filter["services"])==0:
    #         if len(filter["addServices"])==0:
    #             query = { '$and': [ { 'score': { '$gt': 0 } }, { 'status': 'active' } ] }



    # забираем мастеров из базы в соответствии с фильтром; берем только активных; сортируем по убыванию баллам
    masters = list(conf.db.masters.find(query).sort("score", -1))

    result["count"] = len(masters)
    result["masters"] = []
    result["configUrl"] = conf.configUrl

    max_page = int(math.ceil(result["count"]/conf.max_masters_batch))

    begin = (page-1)*conf.max_masters_batch
    end = begin + conf.max_masters_batch

    result["max_page"] = max_page
    result["current_page"] = page

    cut_list_masters = masters[begin:end]

    for master in cut_list_masters:
        bufMaster = {"_id": master["_id"],
                     "name": master["name"],
                     "avatar": master["avatar"],
                     "count_works": len(master["works"])}
        result["masters"].append(bufMaster)

    result["categories"] = list(conf.db.category_job.find())
    result["additionalServicesDict"] = conf.addServicesDict

    return common.JSONEncoder().encode(result)

# API ремонтаса. сервис сравнения мастеров
@route('/api/compareService', method='POST')
def rem_compareMasters():
    result = dict()
    result["configUrl"] = conf.configUrl

    mastersList = []
    masters = []
    categories = []
    servicesMastersSet = set()

    for el in request.json["masters"]:
        mastersList.append(ObjectId(el))

    query = dict()

    query["_id"] = {'$in': mastersList}

    resultMasters = conf.db.masters.find(query)

    for master in resultMasters:
        newMaster=dict()
        newMaster["_id"] = master["_id"]
        newMaster["name"] = master["name"]
        if master["phone1"]!="":
            newMaster["phone"] = master["phone1"]
        else:
            newMaster["phone"] = master["phone2"]
        newMaster["avatar"] = master["avatar"]
        newMaster["count_works"] = len(master["works"])

        newMaster["prices"] = dict()

        for category in master["categories"]:
            for kindService in category["kind_services"]:
                needAddKindService = False
                for service in kindService["services"]:
                    if service["price"]>0:
                        servicesMastersSet.add(service["_id"])
                        newMaster["prices"].update({service["_id"]:service["price"]})
                        needAddKindService = True
                if needAddKindService:
                    servicesMastersSet.add(kindService["_id"])
        masters.append(newMaster)

    kindServicesDict = conf.db.category_job.find({"type": "service"}).sort([("parent_id",-1),("order",-1)])

    for kindService in kindServicesDict:
        if str(kindService["_id"]) in servicesMastersSet:
            newCategory = {'name':kindService["val"], 'type':kindService["type"], '_id':kindService["_id"]}
            categories.append(newCategory)
            servicesList = conf.db.category_job.find({"parent_id": kindService["_id"]}).sort("order",-1)
            for service in servicesList:
                if str(service["_id"]) in servicesMastersSet:
                    newService = {'name': service["val"], 'type': service["type"], '_id': service["_id"], "measure":service["measure"]}
                    categories.append(newService)

    result["categories"] = categories
    result["masters"] = masters


    # a = set({"n":1})

    return common.JSONEncoder().encode(result)

def kindServicesCount(category):
    return conf.db.category_job.find({"parent_id": category["_id"]}).count()

# API ремонтаса. получение данных для личного кабинета
@route('/api/lk')
def rem_lkGetData():
    result_check_rights = adminka.check_rights("master", request)
    if result_check_rights["status"]:
        user = conf.db.users_masters.find_one({"_id": ObjectId(result_check_rights["user_id"])})
        lkResult = {}

        if request.params.method == "init":
            try:
                master = conf.db.masters.find_one({"_id": ObjectId(user["master_id"])})
                if master is not None:
                    lkResult["master"] = master
                    lkResult["categories"] = list(conf.db.category_job.find())
                    lkResult["configUrl"] = conf.configUrl
                    lkResult["scoreDetail"] = conf.db.scoreMasters.find_one({"master_id": ObjectId(user["master_id"])})
                    lkResult["status"] = "OK"
                else:
                    lkResult["status"] = "Error"
                    lkResult["note"] = "id not found"
            except Exception as e:
                    lkResult["status"] = "Error"
                    lkResult["note"] = str(e)
                    print(e)
                    common.writeToLog("error", str(e))

            return common.JSONEncoder().encode(lkResult)

        # elif request.params.method == "123":
        #    pass

    else:
        return abort(401, "Sorry, access denied.")


# API ремонтаса. Сохранение данных
@route('/api/lk', method='POST')
def rem_lkSaveData():
    result_check_rights = adminka.check_rights("master", request)
    if result_check_rights["status"]:
        user = conf.db.users_masters.find_one({"_id": ObjectId(result_check_rights["user_id"])})

        result = {}

        try:
            oldMaster = conf.db.masters.find_one({"_id": ObjectId(user["master_id"])})
            if oldMaster != None:

                newMaster = json.loads(request.forms.get("master"))

                del newMaster["_id"]

                if "email" in newMaster and "email" in oldMaster:
                    newMaster["email"] = oldMaster["email"]
                if "status" in newMaster and "status" in oldMaster:
                    newMaster["status"] = oldMaster["status"]
                if "kind_profile" in newMaster and "kind_profile" in oldMaster:
                    newMaster["kind_profile"] = oldMaster["kind_profile"]
                if "name" in newMaster and "name" in oldMaster:
                    newMaster["name"] = oldMaster["name"]
                if "sername" in newMaster and "sername" in oldMaster:
                    newMaster["sername"] = oldMaster["sername"]
                if "patronymic" in newMaster and "patronymic" in oldMaster:
                    newMaster["patronymic"] = oldMaster["patronymic"]

                avatarFile = request.files.get("avatar")

                if avatarFile is not None:
                    avatarFile.filename = common.createFileName(avatarFile.raw_filename)
                    newMaster["avatar"] = avatarFile.filename

                    avatarFile.save(conf.storage_path)

                    oldFilePath = conf.storage_path + oldMaster["avatar"]
                    if os.path.isfile(oldFilePath):
                        if oldMaster["avatar"] != conf.img_no_avatar:
                            os.remove(oldFilePath)
                    else:  # Show an error ##
                        print("Error: %s file not found" % oldMaster["avatar"])

                common.syncFiles(newMaster, oldMaster, request)

                conf.db.masters.update_one({"_id": ObjectId(user["master_id"])}, {"$set": newMaster})

                common.calcScoreMaster(user["master_id"])

                result["status"] = "OK"

            else:
                raise ValueError('Master id not found.', str(user["master_id"]))

        except Exception as e:
            result["status"] = "Error"
            result["note"] = str(e)
            print("Error: " + str(e))
            common.writeToLog("error", "rem_lkSaveData: " + str(e))

        return result

    else:
        return abort(401, "Sorry, access denied.")


# API ремонтаса. получение данных по мастеру
@route('/api/masterOpenProfile/<masterId>')
def rem_masterGetData(masterId):
    result = dict()

    try:
        master = conf.db.masters.find_one({"_id": ObjectId(masterId)})
        if master is not None:


            # удалим лишние поля
            # if "_id" in master:
            #     del master["_id"]
            if "status" in master:
                del master["status"]
            if "score" in master:
                del master["score"]
            if "email" in master:
                del master["email"]

            result["master"] = clearMasterFromBadData(master)

            result["configUrl"] = conf.configUrl
            result["status"] = "OK"
        else:
            result["status"] = "Error"
            result["note"] = "id not found"
    except Exception as e:
        result["status"] = "Error"
        result["note"] = str(e)
        print(e)
        common.writeToLog("error", "rem_masterGetData: " + str(e))

    return common.JSONEncoder().encode(result)

def clearMasterFromBadData(master):
    # удаляем пустые категории и нулевые услуги

    categoryDeleteList = []
    kindServicesDeleteList = []
    servicesDeleteList = []

    for category in master["categories"]:
        # ищем пустые виды услуг, добавляем в список к удалению
        for kindService in category["kind_services"]:
            for service in kindService["services"]:
                if service["price"]==0:
                    servicesDeleteList.append(service)
            for service in servicesDeleteList:
                kindService["services"].remove(service)
            servicesDeleteList=[]
            if len(kindService["services"]) == 0:
                kindServicesDeleteList.append(kindService)
        # удаляем все виды услуг из списка удаления
        for kindService in kindServicesDeleteList:
            category["kind_services"].remove(kindService)
        kindServicesDeleteList=[]
        if len(category["kind_services"]) == 0:
            categoryDeleteList.append(category)

    for category in categoryDeleteList:
        master["categories"].remove(category)

    return master



@route('/api/masterRegister', method='POST')
def rem_registerMaster():
    # request.json["sername"]

    result = dict()

    try:
    # проверка полноты запроса - есть все необходимые поля
        if not ("kind_profile" in request.json):
            result["status"] = "error"
            result["errorType"] = "fieldMiss"
            result["description"] = "Отсутствует обязательное поле для регистрации: " + "kind_profile"
            return common.JSONEncoder().encode(result)
        else:
            if (request.json["kind_profile"] != "phys") and (request.json["kind_profile"] != "org"):
                result["status"] = "error"
                result["errorType"] = "fieldIncorrect"
                result["description"] = "Некорректно заполнено одно из обязательных полей"
                return common.JSONEncoder().encode(result)

        if (not ("name" in request.json)) or (not ("email" in request.json)) or (not ("password" in request.json)):
            result["status"] = "error"
            result["errorType"] = "fieldMiss"
            result["description"] = "Отсутствует обязательное поле для регистрации"
            return common.JSONEncoder().encode(result)

        if request.json["kind_profile"] == "phys":
            if not ("sername" in request.json):
                result["status"] = "error"
                result["errorType"] = "fieldMiss"
                result["description"] = "Отсутствует обязательное поле для регистрации"
                return common.JSONEncoder().encode(result)

        if len(request.json["email"]) == 0:
            result["status"] = "error"
            result["errorType"] = "emailBlank"
            result["description"] = "Электронная почта не заполнена"
            return common.JSONEncoder().encode(result)

        # проверка емейла - емейл не занят
        if conf.db.users_masters.find({"login": request.json["email"]}).count() > 0:
            result["status"] = "error"
            result["errorType"] = "emailAlreadyRegistered"
            result["description"] = "С указанным ящиком электронной почты уже зарегистрирован мастер"
            return common.JSONEncoder().encode(result)

        # проверка пароля - если пустой, генерировать новый

        # создание мастера в базе данных
        masterUserId = createMaster(request.json, result)
        if masterUserId is None:
            return common.JSONEncoder().encode(result)

        # уведомление по почте
        if not sendNotificationAboutSuccesRegisterToMaster(masterUserId, result):
            return common.JSONEncoder().encode(result)

        result["status"] = "ok"
        return common.JSONEncoder().encode(result)

    except Exception as e:
        print("Error: " + str(e))
        result["status"] = "error"
        result["errorType"] = "unknownError"
        result["description"] = "Непредвиденная ошибка: " + str(e)
        common.writeToLog("error", "rem_registerMaster: " + str(e))
        return common.JSONEncoder().encode(result)


def createMaster(regParams, result):
    try:

        master = {"name": regParams["name"],
                  "status": "new",
                  "score": 0,
                  "avatar": conf.img_no_avatar,
                  "kind_profile": regParams["kind_profile"],
                  "email": regParams["email"],
                  "phone1": "",
                  "phone2": "",
                  "detail": "",
                  "categories": [],
                  "additional_service": [],
                  "works": []
                  }

        if regParams["kind_profile"] == "phys":
            master["sername"] = regParams["sername"]
            master["patronymic"] = regParams["patronymic"]

        resultInsert = conf.db.masters.insert_one(master)

        masterUser = {
                        "login": regParams["email"],
                        "password": regParams["password"],
                        "master_id": ObjectId(resultInsert.inserted_id),
                        "checkEmailCode": common.createEmailCheckCode(),
                        "status": "new"
                    }

        resultInsert = conf.db.users_masters.insert_one(masterUser)

        common.calcScoreMaster(masterUser["master_id"])

        return resultInsert.inserted_id

    except Exception as e:
        print("Error: " + str(e))
        result["status"] = "error"
        result["errorType"] = "unknownError"
        result["description"] = "Непредвиденная ошибка: " + str(e)
        common.writeToLog("error", "createMaster: " + str(e))
        return None


@route('/api/verifyMail/<code>', name="verifyMail")
def rem_checkEmailCode(code):
    try:
        masterUser = conf.db.users_masters.find_one({"checkEmailCode": code})

        if masterUser is not None:
            # master = conf.db.masters.find_one({"_id": masterUser["master_id"]})
            conf.db.masters.update_one({"_id": masterUser["master_id"]}, {"$set": {"status": "register"}})
            # conf.db.users_masters.update_one({"_id": masterUser["_id"]}, {})
            conf.db.users_masters.update_one({"_id": masterUser["_id"]}, {"$unset": {"checkEmailCode": ""}, "$set": {"status": "register"}})
            sendNotificationAboutSuccesVerifyEmail(masterUser["_id"])
    except Exception as e:
        print("Error: " + str(e))
        common.writeToLog("error", "rem_checkEmailCode: " + str(e))

    redirect('/')


def sendNotificationAboutSuccesRegisterToMaster(masterUserId, result):
    try:
        masterUser = conf.db.users_masters.find_one({"_id": ObjectId(masterUserId)})
        master = conf.db.masters.find_one({"_id": masterUser["master_id"]})

        siteURL = request.urlparts[0] + "://" + request.urlparts[1] + url("verifyMail", code=masterUser["checkEmailCode"])

        messageText = conf.messageRegisterMasterText.format(name=master["name"], siteURL=siteURL)
        messageHTML = conf.messageRegisterMasterHTML.format(name=master["name"], siteURL=siteURL)

        subject = "Регистрация на remontas24.ru"

        common.sendMail(masterUser["login"], subject, messageText, messageHTML)

        return True
    except Exception as e:
        print("Error: " + str(e))
        result["status"] = "error"
        result["errorType"] = "unknownError"
        result["description"] = "Непредвиденная ошибка: " + str(e)
        common.writeToLog("error", str(e))
        return False


def sendNotificationAboutSuccesVerifyEmail(masterUserId):
    try:
        masterUser = conf.db.users_masters.find_one({"_id": ObjectId(masterUserId)})
        master = conf.db.masters.find_one({"_id": masterUser["master_id"]})

        siteURL = request.urlparts[0] + "://" + request.urlparts[1]

        messageText = conf.messageVerifyEmailText.format(name=master["name"], siteURL=siteURL)
        messageHTML = conf.messageVerifyEmailHTML.format(name=master["name"], siteURL=siteURL)

        subject = "Доступно заполнение портфолио в remontas24.ru"

        common.sendMail(masterUser["login"], subject, messageText, messageHTML)

        return True
    except Exception as e:
        print("Error: " + str(e))
        common.writeToLog("error", "sendNotificationAboutSuccesVerifyEmail: " + str(e))


@route('/api/masterResetPassword', method='POST')
def rem_resetMasterPassword():
    result = dict()

    try:
        # найти юзера мастера
        masterUser = conf.db.users_masters.find_one({"login": request.json["email"]})
        master = conf.db.masters.find_one({"_id": masterUser["master_id"]})

        # сгенерировать и установить новый пароль

        newPassword = common.generatePassword(8)

        conf.db.users_masters.update_one({"_id": masterUser["_id"]}, {"$set": {"password": newPassword}})

        # отправить уведомление на email

        siteURL = request.urlparts[0] + "://" + request.urlparts[1]

        messageText = conf.messagePasswordRecoveryEmailText.format(name=master["name"], siteURL=siteURL, password=newPassword)
        messageHTML = conf.messagePasswordRecoveryEmailHTML.format(name=master["name"], siteURL=siteURL, password=newPassword)

        subject = "Восстановление пароля на remontas24.ru"

        common.sendMail(masterUser["login"], subject, messageText, messageHTML)

        # вернуть ответ на клиента, что все ок
        result["status"] = "ok"

        return result

    except Exception as e:
        print("Error: " + str(e))
        result["status"] = "error"
        result["errorType"] = "unknownError"
        result["description"] = "Непредвиденная ошибка: " + str(e)
        common.writeToLog("error", "rem_resetMasterPassword: " + str(e))
        return common.JSONEncoder().encode(result)
