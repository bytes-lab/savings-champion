import { combineReducers } from 'redux'
import { SHOW_ADD_PRODUCT, HIDE_ADD_PRODUCT, SHOW_EDIT_PRODUCT, HIDE_EDIT_PRODUCT, ADD_PRODUCT } from './actions'


const initial_product = {
                id: '',
                provider: 'Unknown Provider',
                provider__id: -1,
                product__title: 'Unknown Account',
                product__id: -1,
                product__type: 'Unknown Type',
                balance: 0,
                rate: 0,
                switch__product__increase: 0,
                switch__product__title: 'Unknown Replacement Account',
                creating: true,
                editing: false
};

function product(state = initial_product, action) {
    switch (action.type) {
        case SHOW_ADD_PRODUCT:
            return Object.assign({}, state, {
                creating: true
            });
        case HIDE_ADD_PRODUCT:
            return Object.assign({}, state, {
                creating: false
            });
        case SHOW_EDIT_PRODUCT:
            return Object.assign({}, state, {
                editing: true
            });
        case HIDE_EDIT_PRODUCT:
            return Object.assign({}, state, {
                editing: false
            });
        default:
            return state
    }
}

function products(state = [], action) {
    switch (action.type) {
        case ADD_PRODUCT:
            return [
                ...state,
                product(undefined, action)
            ];
        default:
            return state
    }
}

const ratetrackerState = combineReducers({
    products
});

export default ratetrackerState;

