remontas24Site.controller('lkController', ['$scope', 'lkData', 'masterMainData', function ($scope, lkData, masterMainData) {

    $scope.data = lkData.init({}, function (value, responseHeaders) {
        $scope.masterData = value.master;
        $scope.categories = value.categories;
        $scope.tempMasterCategories = value.master.categories.slice();
        $scope.tempAdditional_service = value.master.additional_service.slice();

    });


    //$scope.masterData = $scope.data["master"];

    $scope.interfaceOptions = {
        showCategory: false,
        showAddServices: false
    };

    $scope.saveMainData = function () {
        var master = {
            detail: $scope.masterData.detail,
            phone1: $scope.masterData.phone1,
            phone2: $scope.masterData.phone2
        };
        masterMainData.save(master);
    }

    // Функции для меню категорий
    $scope.showCategoriesMenu = function () {
        $scope.interfaceOptions.showAddServices = false
        if (!$scope.interfaceOptions.showCategory) {
            $scope.tempMasterCategories = $scope.masterData.categories.slice()
        }
        return $scope.interfaceOptions.showCategory = !$scope.interfaceOptions.showCategory;
    }

    $scope.selectCategories = function () {
        $scope.masterData.categories = $scope.tempMasterCategories.slice();
        $scope.interfaceOptions.showCategory = false;
    }

    $scope.isCheckedCategory = function (element) {
        return $scope.tempMasterCategories.indexOf(element._id) >= 0;
    }


    $scope.checkCategory = function (element) {
        var numberPosition = $scope.tempMasterCategories.indexOf(element._id)
        if (numberPosition >= 0) {
            $scope.tempMasterCategories.splice(numberPosition, 1);
        } else {
            $scope.tempMasterCategories.push(element._id);
        }
    }


    // Функции для меню дополнительных видов работ
    $scope.showAdditionalServiceMenu = function () {
        $scope.interfaceOptions.showCategory = false
        if (!$scope.interfaceOptions.showAddServices) {
            $scope.tempAdditional_service = $scope.masterData.additional_service.slice();
        }
        return $scope.interfaceOptions.showAddServices = !$scope.interfaceOptions.showAddServices;
    }

    $scope.selectAdditionalService = function () {
        $scope.masterData.additional_service = $scope.tempAdditional_service.slice();
        $scope.interfaceOptions.showAddServices = false;
    }

    $scope.isCheckedAdditionalService = function (element) {
        return $scope.tempAdditional_service.indexOf(element) >= 0;
    }

    $scope.checkAdditionalService = function (element) {
        var numberPosition = $scope.tempAdditional_service.indexOf(element)
        if (numberPosition >= 0) {
            $scope.tempAdditional_service.splice(numberPosition, 1);
        } else {
            $scope.tempAdditional_service.push(element);
        }
    }


    $scope.filtrMasterCategories = function (element) {
        if ($scope.masterData.categories.indexOf(element.parent_id) >= 0) {
            return true;
        } else {
            return false;
        }
    }

    $scope.filtrMasterKind_services = function (parentIdElement) {
        return function (elementServices) {
            var filtered = $scope.categories.filter(findById(elementServices._id));
            if (filtered.length > 0) {
                if (filtered[0].parent_id == parentIdElement) {
                    return true;
                }
            }
            return false
        }
    }

    function findById(id) {
        return function (element) {
            return element._id == id;
        }
    }

    $scope.findNameServiceById = function (elementId) {
        var filtered = $scope.categories.filter(findById(elementId));
        if (filtered.length > 0) {
            return filtered[0].val;
        }
        return ""
    }

}]);