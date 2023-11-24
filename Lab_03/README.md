## Отчет о проделанной работе

### 1. Переборщик паролей для формы в задании Bruteforce на сайте dvwa.local

Переборшик паролей исользует список самых частых логинов и 10000
паролей [Источник](https://github.com/danielmiessler/SecLists/blob/master/Passwords/Common-Credentials/10k-most-common.txt)
В случае успеха, программа выводит логин + пароль, иначе пишет о неудачном поиске.

```Успех!
admin:password
```

### 2. Анализ кода

`CWE-326` **Использование устаревшего алгоритма хеширования**

Код использует устаревший алгоритм хеширования MD5 для паролей, что подвергает приложение риску атак на словарь и
коллизии.

`CWE-89` **SQL-инъекции**
Код уязвим к SQL-инъекциям, так как он вставляет значения напрямую из URL-параметров в SQL-запрос без должной фильтрации
или экранирования.

`CWE-307` **Неправильное ограничение чрезмерных попыток аутентификации**

Данный код не предоставляет механизм ограничения количества попыток аутентификации для предотвращения атак перебора
паролей (Brute Force)

### 3. Исправление кода
В качестве защиты выбран метод для ограничения числа неудачных попыток авторизации.


Этот метод использует счетчик неудачных попыток и временной таймаут для ограничения частоты ввода паролей, предотвращая эффективные брутфорс-атаки, при которых злоумышленник многократно пытается угадать пароль, обеспечивая дополнительный слой безопасности. После превышения лимита неудачных попыток, система требует от пользователя ожидания определенного времени перед следующей попыткой входа.

```php
<?php
session_start();

// Определение времени таймаута (в секундах)
$timeout = 60; // Например, таймаут в 1 минуту

if (isset($_SESSION['last_attempt_time']) && time() - $_SESSION['last_attempt_time'] < $timeout) {
    // Вывод сообщения об ожидании
    $remaining_time = $timeout - (time() - $_SESSION['last_attempt_time']);
    $html .= "<pre><br />Too many login attempts. Please wait for {$remaining_time} seconds before trying again.</pre>";
} else {
    if (isset($_GET['Login'])) {
        // Увеличение счетчика попыток
        if (!isset($_SESSION['login_attempts'])) {
            $_SESSION['login_attempts'] = 0;
        }
        $_SESSION['login_attempts']++;

        // Получение данных из формы
        $user = $_GET['username'];
        $pass = $_GET['password'];
        $pass = md5($pass);

        // Проверка в базе данных
        $query = "SELECT * FROM `users` WHERE user = '$user' AND password = '$pass';";
        $result = mysqli_query($GLOBALS["___mysqli_ston"], $query) or die('<pre>' . ((is_object($GLOBALS["___mysqli_ston"])) ? mysqli_error($GLOBALS["___mysqli_ston"]) : (($___mysqli_res = mysqli_connect_error()) ? $___mysqli_res : false)) . '</pre>');

        if ($result && mysqli_num_rows($result) == 1) {
            // Успешный вход
            $row = mysqli_fetch_assoc($result);
            $avatar = $row["avatar"];
            $html .= "<p>Welcome to the password protected area {$user}</p>";
            $html .= "<img src=\"{$avatar}\" />";
            // Сброс счетчика попыток при успешном входе
            $_SESSION['login_attempts'] = 0;
        } else {
            // Неверный вход
            $html .= "<pre><br />Username and/or password incorrect.</pre>";

            // Запись времени последней попытки
            $_SESSION['last_attempt_time'] = time();
        }

        ((is_null($___mysqli_res = mysqli_close($GLOBALS["___mysqli_ston"]))) ? false : $___mysqli_res);
    }
}


```