// https://github.com/botui/botui

var botui = new BotUI("app"); // id of container
const socket = io("http://localhost:5005");
var message_idx = [];
var message_time = [];

/**
 * Called upon loading the webpage and greets the user.
 */
function init() {
  // websocket init to receive messages
  receiveMsg();
  // show greeting messages to user
  botui.message
    .bot({
      delay: 200,
      content: "Hallo, ich bin ein Bot!",
    })
    .then(function () {
      botui.message.bot({
        delay: 1000, // wait 1 sec.
        loading: true,
        content:
          "Ich kann dir bei verschiedensten Angelegenheiten rund ums Bürgeramt helfen. Frag mich einfach etwas.",
      });
    });
}

/**
 * Sends a message to the rasa server through a websocket channel.
 * @param {*} msg
 */
async function sendMsg(msg) {
  socket.emit("user_uttered", {
    message: msg,
  });
}

/**
 * The functions registers the receive channel of the websocket connection
 * to the rasa server backend.
 */
function receiveMsg() {
  socket.on("bot_uttered", function (response) {
    m_index = message_idx.shift();
    m_time = message_time.shift();
    curr_time = Date.now();
    time_diff = curr_time - m_time;
    if (response.text) {
      // if an additional is received
      if (m_index === undefined) {
        botui.message.add({
          delay: 1000,
          loading: true,
          content: response.text,
        });
      } else {
        // if delay is more than 1 second, display immediately
        if (time_diff > 1000) {
          botui.message.update(m_index, {
            loading: false,
            content: response.text,
          });
        } else {
          // delay display of requested bot response, min. of 1 second
          setTimeout(
            function (idx, text) {
              console.log(text);
              botui.message.update(idx, {
                loading: false,
                content: text,
              });
            },
            1000 - time_diff,
            m_index,
            response.text
          );
        }
      }
    }
    if (response.quick_replies) {
      handleButtons(response);
    }
  });
}

/**
 * This function handles button responses by the rasa server.
 * @param {*} response
 */
function handleButtons(response) {
  buttons = [];
  for (let i = 0; i < response.quick_replies.length; i++) {
    title = response.quick_replies[i]["title"];
    payload = response.quick_replies[i]["payload"];
    msg = {
      text: title,
      value: payload,
    };
    buttons.push(msg);
  }
  botui.action
    .button({
      action: buttons,
    })
    .then(function (res) {
      sendMsg(res.value);
    });
}

/**
 * Creates a permanent text input field.
 */
function showTextInput() {
  const div = document.createElement("div");
  div.className = "text-outer-wrapper";
  div.innerHTML = `
    <div class="text-input-container">
      <div class="text-input-inner">
        <form onsubmit="sendUserText();return false" class="">
          <input autocomplete="off" placeholder="Hier Text eingeben..." required="required" class="text-input-inner-field" id="user"> 
          <button type="button" class="text-input-inner-submit" onclick="sendUserText()">
            <img src="./senden.png" width="14" height="14">
          </button>
        </form>
      </div>
    </div>
  `;
  document.getElementById("main-container").appendChild(div);
}

/**
 * Sends a user message to the server.
 */
function sendUserText() {
  text = document.getElementById("user").value;
  botui.message.add({
    human: true,
    content: text,
  });
  botui.message
    .add({
      loading: true,
    })
    .then(function (index) {
      message_idx.push(index);
      message_time.push(Date.now());
    });

  sendMsg(text);
  document.getElementById("user").value = "";
}

/**
 * Initialize BotUI when page is successfully loaded.
 */
document.addEventListener("DOMContentLoaded", function (event) {
  // bot init
  init();
  showTextInput();
});
