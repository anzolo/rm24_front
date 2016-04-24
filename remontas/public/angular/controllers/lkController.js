remontas24Site.controller('lkController', ['$scope', 'lkData', 'masterMainData', '$sce', 'ModalService', 'Upload', '$document', function ($scope, lkData, masterMainData, $sce, ModalService, Upload, $document) {

    $scope.interfaceOptions = {
        showComboBox: "",
        newAvatar: null,
        mouseOverWork: {},
        checkKind_services: null,
        countServices: 0,
        countJobs: 0,
        loading: false,
        textIsChange: "",
        showWhatIs:false
    };

    $scope.tempMasterCategoriesSelect = [];

    $scope.data = {
        "uploadData": {}
    }

    $scope.saveMaster = saveMaster;
    $scope.showCategoriesMenu = showCategoriesMenu;
    $scope.checkAdditionalService = checkAdditionalService;
    $scope.isCheckedCategory = isCheckedCategory;
    $scope.isCheckedAdditionalService = isCheckedAdditionalService;
    $scope.showAdditionalServiceMenu = showAdditionalServiceMenu;
    $scope.selectAdditionalService = selectAdditionalService;
    $scope.preparePriceHTML = preparePriceHTML;
    $scope.selectKindServices = selectKindServices;
    $scope.compareOrder = compareOrder;
    $scope.changeServices = changeServices;
    $scope.onlyMasterCategory = onlyMasterCategory;

    $scope.checkCategory = checkCategory;
    $scope.selectCategories = selectCategories;
    $scope.changeAvatar = changeAvatar;
    $scope.getImgLink = getImgLink;
    $scope.editWorks = editWorks;
    $scope.isFirstPhotoNew = isFirstPhotoNew;
    $scope.shrinkText = shrinkText;
    $scope.changeText = changeText;

    loadData();

    /////////////////////////////////////////////////////////////////////////

    //загрузка и сохранение

    function loadData() {
        lkData.init({}, function (data) {
            if (data.status == "OK") {
                $scope.data.master = JSON.parse(JSON.stringify(data.master));

                $scope.data.configUrl = JSON.parse(JSON.stringify(data.configUrl));

                $scope.data.categories = JSON.parse(JSON.stringify(data.categories));

                $scope.data.kind_services = masterKindServiceArray();

                $scope.data.scoreDetail = JSON.parse(JSON.stringify(data.scoreDetail.details));

                calcCountServices();

            } else if (data.status == "Error") {
                console.error("Error:", data.note);
                //                $state.go('adminka.masters');
            }
        });
    }

    function saveMaster() {
        $scope.loading = true;

        var connString = '/api/lk';

        if ($scope.data.master.phone1 == undefined) $scope.data.master.phone1 = ""
        if ($scope.data.master.phone2 == undefined) $scope.data.master.phone2 = ""

        $scope.data.uploadData.master = Upload.json($scope.data.master);

        Upload.upload({
            url: connString,
            data: $scope.data.uploadData

        }).then(function (resp) {
            loadData();
        }, function (resp) {
            console.log('Error status: ' + resp.status);
        }).finally(function () {
            // called no matter success or failure
            $scope.loading = false;
        });;

    };

    //изменение аватарки

    function changeAvatar() {
        if ($scope.interfaceOptions.showComboBox != "") return;
        var bodyRef = angular.element($document[0].body)
        bodyRef.addClass('ovh'); // перенести в модальное окно аватарки

        ModalService.showModal({
            templateUrl: "/remontas/public/templates/modals/changeAvatar.html",
            controller: "changeAvatarModalController"
        }).then(function (modal) {
            modal.close.then(function (result) {
                $scope.data.uploadData.avatar = result;
                bodyRef.removeClass('ovh');
                saveMaster();
            });
        });
    }

    // Функции для меню категорий
    function showCategoriesMenu() {
        if ($scope.interfaceOptions.showComboBox == "") {
            $scope.tempMasterCategoriesSelect = $scope.data.master.categories.slice();
            $scope.interfaceOptions.showComboBox = "Category";
        }
    }

    function selectCategories() {
        //$scope.masterData.categories = $scope.tempMasterCategoriesSelect.slice();
        $scope.interfaceOptions.showComboBox = "";
        $scope.data.kind_services = masterKindServiceArray();
        calcCountServices();
        saveMaster();
    }

    function isCheckedCategory(element) {
        return $scope.data.master.categories.findIndex(function (el) {
            return el._id == element._id;
        }) >= 0;
    };

    function checkCategory(element) {
        var categoryIndex = $scope.data.master.categories.findIndex(function (el) {
            return el._id == element._id
        });

        if (categoryIndex >= 0) {
            $scope.data.master.categories.splice(categoryIndex, 1);
            $scope.data.kind_services = masterKindServiceArray();
        } else if ($scope.data.master.categories.length < 2) {
            var tempcategoryIndex = $scope.tempMasterCategoriesSelect.findIndex(function (el) {
                return el._id == element._id
            });

            if (tempcategoryIndex >= 0) {
                $scope.data.master.categories.push($scope.tempMasterCategoriesSelect[tempcategoryIndex]);
            } else {
                // var categoryDict = $scope.categories.find();

                var newCategory = {
                    "_id": element._id,
                    "name": element.val,
                    "order": element.order,
                    "kind_services": []
                };
                $scope.data.master.categories.push(newCategory);
            }
            $scope.data.kind_services = masterKindServiceArray();
        }
    }


    // Функции для меню дополнительных видов работ
    function checkAdditionalService(element) {
        var categoryIndex = $scope.data.master.additional_service.indexOf(element);

        if (categoryIndex >= 0) {
            $scope.data.master.additional_service.splice(categoryIndex, 1);
        } else {
            // var categoryDict = $scope.categories.find();
            $scope.data.master.additional_service.push(element);
        }
    }

    function isCheckedAdditionalService(element) {
        return $scope.data.master.additional_service.indexOf(element) >= 0
    }

    function showAdditionalServiceMenu() {
        if ($scope.interfaceOptions.showComboBox == "") {
            $scope.interfaceOptions.showComboBox = 'AddServices';
        }
    }

    function selectAdditionalService() {
        //        $scope.masterData.additional_service = $scope.tempAdditional_service.slice();
        $scope.interfaceOptions.showComboBox = "";
        saveMaster();
    }


    // Функции для блока "услуги"
    function preparePriceHTML(price, measure) {
        var newValue = $sce.trustAsHtml(price + " " + measure);
        return newValue;
    };

    function selectKindServices(id) {
        if ($scope.interfaceOptions.checkKind_services != id) $scope.interfaceOptions.checkKind_services = id;
        else $scope.interfaceOptions.checkKind_services = null
    }

    function compareOrder(a, b) {
        if (a.order < b.order) return -1;
        else if (a.order > b.order) return 1;
        else return 0;
    }

    function onlyMasterCategory() {
        return function (category) {
            return $scope.data.master.categories.findIndex(function (el) {
                return el._id == category._id
            }) >= 0
        };
    };

    function masterKindServiceArray() {
        var result = [];
        var category = $scope.data.categories.filter(function (el) {
            return (el.type == 'category') && categoryInMaster(el)
        }).sort($scope.compareOrder);

        category.forEach(function (cat, i, arr) {
            var kindService = $scope.data.categories.filter(function (el) {
                return el.parent_id == cat._id
            }).sort($scope.compareOrder);

            kindService.forEach(function (kser, i, arr) {
                var kindServiceM = KindServiceInMaster(cat, kser);
                if (kindServiceM != undefined) result.push(kindServiceM)
                else {
                    var newKindService = {
                        "_id": kser._id,
                        "name": kser.val,
                        "order": kser.order,
                        "services": []
                    };
                    result.push(newKindService)
                }
            });
        });
        //        console.log(result)
        return result;
    };

    function categoryInMaster(category) {
        return $scope.data.master.categories.findIndex(function (el) {
            return el._id == category._id
        }) >= 0
    };

    function KindServiceInMaster(category, KindService) {
        var categoryIndex = $scope.data.master.categories.findIndex(function (el) {
            return el._id == category._id
        });
        if (categoryIndex >= 0) {
            var kindServiceIndex = $scope.data.master.categories[categoryIndex].kind_services.findIndex(function (el) {
                return el._id == KindService._id
            });

            if (kindServiceIndex >= 0) return $scope.data.master.categories[categoryIndex].kind_services[kindServiceIndex]
            else return undefined;
        } else return undefined;
    };

    function changeServices(kindService) {
        if ($scope.interfaceOptions.showComboBox != "") return;
        //        $scope.bodyRef = angular.element(document.querySelector('.my'))
        //         angular.element(document.getElementsByClassName("multi-files"));
        var bodyRef = angular.element($document[0].body)
        bodyRef.addClass('ovh');
        ModalService.showModal({
            templateUrl: "/remontas/public/templates/modals/changeServices.html",
            controller: "changeServicesModalController",
            inputs: {
                data: {
                    kindService_id: kindService._id,
                    categories: $scope.data.categories,
                    master: $scope.data.master
                }
            }
        }).then(function (modal) {
            modal.close.then(function (result) {
                bodyRef.removeClass('ovh');
                $scope.data.kind_services = masterKindServiceArray();
                calcCountServices();
                saveMaster();
            });
        });
    }

    function calcCountServices() {
        var count = 0;

        $scope.data.master.categories.forEach(function (category, i, arr) {
            category.kind_services.forEach(function (kindService, i, arr) {
                kindService.services.forEach(function (service, i, arr) {
                    count++;
                })
            })
        });

        $scope.interfaceOptions.countServices = count;
    }


    // функции для блока "Работы"

    function shrinkText(title) {
        if (title.length > 50) {
            return title.substring(0, 50) + "..."
        } else return title;
    }

    function getImgLink(work) {
        var result;

        if (work.photos.length > 0) {
            if (work.photos[0]["new"]) result = $scope.data.uploadData[work.photos[0].filename]
            else result = $scope.data.configUrl.img_url_work_path + work.photos[0].filename;
        }

        return result;
    }

    function isFirstPhotoNew(work) {
        if (work.photos.length > 0) {
            return work.photos[0]["new"];
        } else {
            return false;
        }
    }

    function editWorks(work) {
        if ($scope.interfaceOptions.showComboBox != "") return;
        var bodyRef = angular.element($document[0].body)
        bodyRef.addClass('ovh');

        var data = {
            //                    kindService: kindService,
            //                    categories: $scope.data.categories,
            master: $scope.data.master,
            configUrl: $scope.data.configUrl,
            uploadData: $scope.data.uploadData
        };

        if (work != undefined) data.editedWork = work;

        ModalService.showModal({
            templateUrl: "/remontas/public/templates/modals/lkWorkManage.html",
            controller: "lkWorkManageController",
            inputs: {
                data: data
            }
        }).then(function (modal) {
            modal.close.then(function (result) {
                bodyRef.removeClass('ovh');
                saveMaster();
            });
        });
    }

    function changeText(element) {
        if ($scope.interfaceOptions.textIsChange == element) {
            $scope.interfaceOptions.textIsChange = '';
            saveMaster();
        }
    }

}]);
