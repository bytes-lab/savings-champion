import React, { Component } from 'react'
import { connect } from 'react-redux'
import Product from '../components/product'
import ProductList from '../components/product_list'
import { addProductToList } from '../actions'
class App extends Component {

    render() {
        const { dispatch, products } = this.props;
        return (
            <div className="container-fluid">
                <div className="col-sm-3">
                    <button onClick={dispatch(addProductToList())}>Add Product</button>
                </div>
                <div className="col-sm-9">
                    <ProductList products={products}/>
                </div>
            </div>
        )
    }
}

function select(state) {
    return {
        products: state.products
    }
}

export default connect(select)(App)