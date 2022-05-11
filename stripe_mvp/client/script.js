// A reference to Stripe.js
var stripe;

var orderData = {
  currency: "usd",
};

var products = [];

fetch("/stripe-key")
  .then(function(result) {
    return result.json();
  })
  .then(function(data) {
    return setupElements(data);
  })
  .then(function({ stripe, card, clientSecret }) {
    document.querySelector("#submit").addEventListener("click", function(evt) {
      evt.preventDefault();
      pay(stripe, card, clientSecret);
    });
    document.querySelector("#submit-off-session").addEventListener("click", function(evt) {
      payOffSession();
    });
  });

fetch("/subscriptions")
  .then(function(result) {
    return result.json();
  })
  .then(function(data) {
    setupProductOptions(data);
    updatePurchaseInfo();
  });

const orderAmount = document.querySelector('.order-amount');
const orderDetails = document.querySelector('.order-details');
const productsSelect = document.querySelector("#product-choice");
const selectOptionTemplate = document.querySelector("#select-option").content;

var buildSelectOption =  function(optionInfo) {
  const option = selectOptionTemplate.firstElementChild.cloneNode(true);
  option.textContent = optionInfo.name;
  option.value = optionInfo.id;

  return option;
}

var setupProductOptions = function(data) {
  data.forEach(optionData => {
    option = buildSelectOption(optionData);
    productsSelect.append(option);
    products.push(optionData);
  })
}

productsSelect.addEventListener('change', evt => {
  updatePurchaseInfo();
});

var updatePurchaseInfo = function() {
  const product = chosenProduct();
  if (!product) {
    return;
  }

  orderAmount.textContent = `$${product.price}.00`;
  orderDetails.textContent = `Purchase ${product.name}`;
}

var chosenProduct = function() {
  return productsSelect.selectedIndex !== -1 ? products[productsSelect.selectedIndex] : null;
}

var setupElements = function(data) {
  stripe = Stripe(data.publicKey);
  /* ------- Set up Stripe Elements to use in checkout form ------- */
  var elements = stripe.elements();
  var style = {
    base: {
      color: "#32325d",
      fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
      fontSmoothing: "antialiased",
      fontSize: "16px",
      "::placeholder": {
        color: "#aab7c4"
      }
    },
    invalid: {
      color: "#fa755a",
      iconColor: "#fa755a"
    }
  };

  var card = elements.create("card", { style: style });
  card.mount("#card-element");

  return {
    stripe,
    card,
    clientSecret: data.clientSecret
  };
};

var handleAction = function(clientSecret) {
  // Show the authentication modal if the PaymentIntent has a status of "requires_action"
  stripe.handleCardAction(clientSecret).then(function(data) {
    if (data.error) {
      showError("Your card was not authenticated, please try again");
    } else if (data.paymentIntent.status === "requires_confirmation") {
      // Card was properly authenticated, we can attempt to confirm the payment again with the same PaymentIntent
      fetch("/users/alice/payments", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          action: 'confirm',
          paymentId: data.paymentIntent.id
        })
      })
        .then(function(result) {
          return result.json();
        })
        .then(function(json) {
          if (json.error) {
            showError(json.error);
          } else {
            orderComplete(clientSecret, 'on-session');
          }
        });
    }
  });
};

var payOffSession = function() {
  var repeatedOrder = {
    currency: orderData.currency,
    item: orderData.item,
    action: 'repeat'
  };

  changeLoadingState(true, 'off-session');

  fetch("/users/alice/payments", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(repeatedOrder)
  })
  .then(function(result) {
    return result.json();
  })
  .then(function(data) {
    changeLoadingState(false, 'off-session');
    if (data.error && data.error === "authentication_required") {
      // Card needs to be authenticatied
      // Send user a message asking him for authentication
    } else if (data.error) {
      // Card was declined off-session
      // Send user a message asking him for a new card
    } else {
      // Card was successfully charged off-session
      orderComplete(data.clientSecret, 'off-session');
    }
  });
}

/*
 * Collect card details and pay for the order 
 */
var pay = function(stripe, card) {
  var cardholderName = document.querySelector("#name").value;
  var data = {
    billing_details: {}
  };

  if (cardholderName) {
    data["billing_details"]["name"] = cardholderName;
  }

  changeLoadingState(true, 'on-session');

  // Collect card details
  stripe
    .createPaymentMethod("card", card, data)
    .then(function(result) {
      if (result.error) {
        showError(result.error.message);
      } else {
        const product = chosenProduct();
        orderData.item = {
          'type': product.type,
          'id': product.id
        }
        orderData.paymentMethodId = result.paymentMethod.id;
        orderData.action = 'create';

        return fetch("/users/alice/payments", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify(orderData)
        });
      }
    })
    .then(function(result) {
      return result.json();
    })
    .then(function(paymentData) {
      if (paymentData.requiresAction) {
        // Request authentication
        handleAction(paymentData.clientSecret);
      } else if (paymentData.error) {
        showError(paymentData.error);
      } else {
        orderComplete(paymentData.clientSecret, 'on-session');
      }
    });
};

/* ------- Post-payment helpers ------- */

/* Shows a success / error message when the payment is complete */
var orderComplete = function(clientSecret, viewTypeClass) {
  stripe.retrievePaymentIntent(clientSecret).then(function(result) {
    var paymentIntent = result.paymentIntent;
    var paymentIntentJson = JSON.stringify(paymentIntent, null, 2);
    document.querySelectorAll(`.payment-view.${viewTypeClass}`).forEach(function(view) {
      view.classList.add("hidden");
    });
    document.querySelectorAll(`.completed-view.${viewTypeClass}`).forEach(function(view) {
      view.classList.remove("hidden");
    });
    document.querySelector(`.status.${viewTypeClass}`).textContent =
      paymentIntent.status === "succeeded" ? "succeeded" : "failed";
    document.querySelector(`pre.${viewTypeClass}`).textContent = paymentIntentJson;
  });
};

var showError = function(errorMsgText) {
  changeLoadingState(false, 'on-session');
  var errorMsg = document.querySelector(".sr-field-error");
  errorMsg.textContent = errorMsgText;
  setTimeout(function() {
    errorMsg.textContent = "";
  }, 4000);
};

// Show a spinner on payment submission
var changeLoadingState = function(isLoading, viewTypeClass) {
  paymentView = document.querySelector(`.payment-view.${viewTypeClass}`);
  if (isLoading) {
    paymentView.querySelector("button").disabled = true;
    paymentView.querySelector("#spinner").classList.remove("hidden");
    paymentView.querySelector("#button-text").classList.add("hidden");
  } else {
    paymentView.querySelector("button").disabled = false;
    paymentView.querySelector("#spinner").classList.add("hidden");
    paymentView.querySelector("#button-text").classList.remove("hidden");
  }
};
