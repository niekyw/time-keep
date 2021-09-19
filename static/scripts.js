let expanded = false;

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

let hr = 0;
let min = 0;
let sec = 0;
let stoptime = true;

function clockIn() {
  try {
    logTaskStart('user', 'task', 'category') //TODO: fix default values
  }catch (error) {
    console.error("Could not log starting task, breaking");
    return;
  }
  if (!logTaskStart("user", "task", "category")) {

  }
  if (stoptime === true) {
        stoptime = false;
        timerCycle();
    }
}
//Does this exist?
function stopTimer() {

  if (stoptime === false) {
    stoptime = true;
  }



}

async function resetTimer() {
    if (!await logTaskEnd('user', 'task', 'category')) {
      alert("Alert could not log starting task, breaking");
    }
    stoptime = true;
    timer.innerHTML = '00:00:00';
    hr = 0;
    min = 0;
    sec = 0;
}

function timerCycle() {
    if (!stoptime) {
    sec = parseInt(sec);
    min = parseInt(min);
    hr = parseInt(hr);

    sec = sec + 1;

    if (sec === 60) {
      min = min + 1;
      sec = 0;
    }
    if (min === 60) {
      hr = hr + 1;
      min = 0;
      sec = 0;
    }

    if (sec < 10 || sec === 0) {
      sec = '0' + sec;
    }
    if (min < 10 || min === 0) {
      min = '0' + min;
    }
    if (hr < 10 || hr === 0) {
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
async function getUserTasks(user, minTime, maxTime) {
    const params = {
        "min_time": minTime,
        "max_time": maxTime,
    };
    // TODO: include categories filter?
    const response = await fetch(
        "/tasks/" + user + formatParams(params)
    );
    if (response.status !== 200) {
        throw Error("Failed to get user tasks");
    }
    return response.json();
}


/**
 * Log a task starting, returning true if the task started successfully and false otherwise.
 *
 * @param user username; str
 * @param task task being done; str
 * @param category category of the task; str | None
 * @return true if succeeded, false otherwise
 */
async function logTaskStart(user, task, category) {
    const params = {
        "task_name": task,
        "category": category,
    };
    const response = await fetch(
        "/tasks/start/" + user + formatParams(params),
        {
            method: "POST",
            body: "",
        },
    )
    return response.status === 201;

}

/**
 * Log a task ending, returning true if the task ended successfully and false otherwise.
 *
 * @param user username; str
 * @return true if succeeded, false otherwise
 */
async function logTaskEnd(user) {
    const response = await fetch(
        "/tasks/end/" + user,
        {
            method: "POST",
            body: "",
        },
    )
    return response.status === 201;
}


/**
 * Get the categories `username` has registered.
 *
 * @param user username; str
 * @return categories that username has registered
 * @throws Error if fails to get categories
 */
async function getCategories(user) {
    const response = await fetch(
        "/categories/" + user
    );
    if (response.status !== 200) {
        throw Error("Failed to get user categories");
    }
    return response.json();
}


/**
 * Add the category `category` as `user`.
 *
 * @param user username; str
 * @param category new category to register
 * @return true if succeeded, false otherwise
 */
async function addCategory(user, category) {
    const params = {
        "category": category
    };
    const response = await fetch(
        "/categories/" + user + formatParams(params),
        {
            method: "POST",
            body: "",
        }
    );
    return response.status === 201;

}

/**
 * Return a JSON object representing a plot of the user's tasks fitting the given constraints.
 *
 * @param user username; str
 * @param minTime minimum time; iso date string | null
 * @param maxTime maximum time; iso date string | null
 * @return list of user tasks within the specified time range
 * @throws Error if cannot get list of user tasks
 */
async function getUserPlots(user, minTime, maxTime) {
    const params = {
        "min_time": minTime,
        "max_time": maxTime,
    };
    const response = await fetch(
        "/plots/" + user + formatParams(params)
    );
    if (response.status !== 200) {
        throw Error("Failed to get user categories");
    }
    return response.json();
}