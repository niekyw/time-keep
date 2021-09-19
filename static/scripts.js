var expanded = false;
const url = "127.0.0.1:8000";

function showCheckboxes() {
  var checkboxes = document.getElementById("checkboxes");
  if (!expanded) {
    checkboxes.style.display = "block";
    expanded = true;
  } else {
    checkboxes.style.display = "none";
    expanded = false;
  }
}


const timer = document.getElementById('stopwatch');

var hr = 0;
var min = 0;
var sec = 0;
var stoptime = true;

function clockIn() {

  if (stoptime == true) {
        stoptime = false;
        timerCycle();
    }
}

function stopTimer() {
  if (stoptime == false) {
    stoptime = true;
  }
}

function resetTimer() {
    stoptime = true;
    timer.innerHTML = '00:00:00';
    hr = 0;
    min = 0;
    sec = 0;
}

function timerCycle() {
    if (stoptime == false) {
    sec = parseInt(sec);
    min = parseInt(min);
    hr = parseInt(hr);

    sec = sec + 1;

    if (sec == 60) {
      min = min + 1;
      sec = 0;
    }
    if (min == 60) {
      hr = hr + 1;
      min = 0;
      sec = 0;
    }

    if (sec < 10 || sec == 0) {
      sec = '0' + sec;
    }
    if (min < 10 || min == 0) {
      min = '0' + min;
    }
    if (hr < 10 || hr == 0) {
      hr = '0' + hr;
    }

    timer.innerHTML = hr + ':' + min+ ':' + sec;

    setTimeout("timerCycle()", 1000);
  }
}


function formatParams(params){
  return "?" + Object
        .keys(params)
        .map(function(key){
          return key+"="+encodeURIComponent(params[key])
        })
        .join("&")
}


/**
 * Get a list of tasks the user has completed within the given time range.
 *
 * @param user username; str
 * @param minTime minimum time; iso date string | null
 * @param maxTime maximum time; iso date string | null
 * @return list of user tasks within the specified time range
 * @throws Error if cannot get list of user tasks
 */
function getUserTasks(user, minTime, maxTime) {
    const xhttp = new XMLHttpRequest();
    const params = {
        "min_time": minTime,
        "max_time": maxTime,
    };
    // TODO: include categories filter?
    xhttp.open("GET", url + "/tasks/" + user + formatParams(params), false);
    xhttp.send()
    xhttp.onreadystatechange = (e) => {
        if (xhttp.status !== 200) {
            throw Error("Failed to get user tasks");
        }
        return JSON.parse(xhttp.responseType);
    }
}


/**
 * Log a task starting, returning true if the task started successfully and false otherwise.
 *
 * @param user username; str
 * @param task task being done; str
 * @param category category of the task; str | None
 * @return true if succeeded, false otherwise
 */
function logTaskStart(user, task, category) {
    const xhttp = new XMLHttpRequest();
    const params = {
        "task_name": task,
        "category": category,
    };
    xhttp.open("POST", url + "/tasks/start/" + user + formatParams(params), false);
    xhttp.send();
    xhttp.onreadystatechange = (e) => {
        return xhttp.status === 201;
    }
}

/**
 * Log a task ending, returning true if the task ended successfully and false otherwise.
 *
 * @param user username; str
 * @return true if succeeded, false otherwise
 */
function logTaskEnd(user) {
    const xhttp = new XMLHttpRequest();
    xhttp.open("POST", url + "/tasks/end/" + user, false);
    xhttp.send();
    xhttp.onreadystatechange = (e) => {
        return xhttp.status === 201;
    }
}


/**
 * Get the categories `username` has registered.
 *
 * @param user username; str
 * @return categories that username has registered
 * @throws Error if fails to get categories
 */
function getCategories(user) {
    const xhttp = new XMLHttpRequest();
    xhttp.open("GET", url + "/categories/" + user, false);
    xhttp.send()
    xhttp.onreadystatechange = (e) => {
        if (xhttp.status !== 200) {
            throw Error("Failed to get categories");
        }
        return JSON.parse(xhttp.responseText);
    }
}


/**
 * Add the category `category` as `user`.
 *
 * @param user username; str
 * @param category new category to register
 * @return true if succeeded, false otherwise
 */
function addCategory(user, category) {
    const xhttp = new XMLHttpRequest();
    const params = {
        "category": category
    };
    xhttp.open("POST", url + "/categories/" + user, false);
    xhttp.send();
    xhttp.onreadystatechange = (e) => {
        return xhttp.status === 201;
    }
}
