import React from 'react';
import { ReactDom, render } from 'react-dom';
import { createStore } from 'redux';
import { Immutable } from 'immutable';
import ratetrackerState from './reducers';
import { Provider } from 'react-redux'
import App from './containers/app'

let store = createStore(ratetrackerState);

let rootElement = document.getElementById('content');

render(
  <Provider store={store}>
    <App />
  </Provider>,
  rootElement
);