<!DOCTYPE html>
<html lang="ru">

<head>
    <base href="/">
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- The above 3 meta tags *must* come first in the head; any other head content must come *after* these tags -->

    <title>Админка Ремонтас24</title>

    <!-- Bootstrap core CSS -->
    <link href="adminka/public/css/bootstrap.min.css" rel="stylesheet">

    <!-- IE10 viewport hack for Surface/desktop Windows 8 bug -->
    <link href="adminka/public/css/ie10-viewport-bug-workaround.css" rel="stylesheet">

    <!-- Custom styles for this template -->
    <link href="adminka/public/css/signin.css" rel="stylesheet">

    <!-- Custom Fonts -->
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.5.0/css/font-awesome.min.css">

    <!-- MetisMenu CSS -->
    <link href="/adminka/public/css/metisMenu.min.css" rel="stylesheet">

    <!-- Timeline CSS -->
    <link href="/adminka/public/css/timeline.css" rel="stylesheet">

    <!-- Custom CSS -->
    <link href="/adminka/public/css/sb-admin-2.css" rel="stylesheet">

    <!-- Morris Charts CSS -->
    <link href="/adminka/public/css/morris.css" rel="stylesheet">


    <!-- HTML5 shim and Respond.js for IE8 support of HTML5 elements and media queries -->
    <!--[if lt IE 9]>
      <script src="https://oss.maxcdn.com/html5shiv/3.7.2/html5shiv.min.js"></script>
      <script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
    <![endif]-->

    <script src="/adminka/public/bower_components/angular/angular.min.js"></script>
    <script src="/adminka/public/bower_components/angular-route/angular-route.min.js"></script>
    <script src="/adminka/public/bower_components/ngstorage/ngStorage.min.js"></script>

</head>

<body ng-app="remontas24App">

    <div ng-controller="mainController">
        <div ng-if="isAuthorizedAdmin">
            <ng-view></ng-view>
        </div>
        <div ng-if="!isAuthorizedAdmin">
            <div class="container">

                <form class="form-signin" ng-submit="login(credentials)" novalidate>
                    <h2 class="form-signin-heading">Введите логин и пароль</h2>
                    <label for="inputEmail" class="sr-only">Электронная почта</label>
                    <input type="email" id="inputEmail" class="form-control" ng-model="credentials.username" placeholder="Адрес электронной почты" required autofocus>
                    <label for="inputPassword" class="sr-only">Пароль</label>
                    <input type="password" id="inputPassword" class="form-control" ng-model="credentials.password" placeholder="Пароль" required>
                    <button class="btn btn-lg btn-primary btn-block" type="submit">Войти</button>
                </form>

            </div>
        </div>
    </div>


    <!-- IE10 viewport hack for Surface/desktop Windows 8 bug -->
    <script src="adminka/public/js/ie10-viewport-bug-workaround.js"></script>

    <!-- Angular Modules -->
    <script src="/adminka/public/app/remontas24App.js"></script>

    <!-- Angular Controllers -->
    <script src="/adminka/public/app/controllers/mainController.js"></script>
    <script src="/adminka/public/app/controllers/adminkaMainPageController.js"></script>

    <!--  Angular services  -->
    <script src="/adminka/public/app/services/AuthServices.js"></script>


    <!-- Доп скрипиты для админки -->
    <script src="/adminka/public/js/jquery-2.1.4.min.js"></script>

    <!-- Bootstrap Core JavaScript -->
    <script src="/adminka/public/js/bootstrap.min.js"></script>

    <!-- Metis Menu Plugin JavaScript -->
    <script src="/adminka/public/js/metisMenu.min.js"></script>

    <!-- Morris Charts JavaScript -->
    <script src="/adminka/public/js/raphael-min.js"></script>
    <script src="/adminka/public/js/morris.min.js"></script>

    <!-- Custom Theme JavaScript -->
    <script src="/adminka/public/js/sb-admin-2.js"></script>

</body>

</html>