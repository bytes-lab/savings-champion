import React, { Component, PropTypes } from 'react'

export default class ProductList extends Component {

    render() {
        {this.props.products.map(product =>
          <Product
            key={product.id}
            {...product} />
        )}
    }

}