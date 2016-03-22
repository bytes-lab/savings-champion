export const SHOW_ADD_PRODUCT = 'SHOW_ADD_PRODUCT';
export const HIDE_ADD_PRODUCT = 'HIDE_ADD_PRODUCT';
export const SHOW_EDIT_PRODUCT = 'SHOW_EDIT_PRODUCT';
export const HIDE_EDIT_PRODUCT = 'HIDE_EDIT_PRODUCT';
export const ADD_PRODUCT = 'ADD_PRODUCT';

export function addProductToList() {
    return {
        type: ADD_PRODUCT
    }
}