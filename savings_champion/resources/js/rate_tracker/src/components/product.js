import React, { Component, PropTypes } from 'react'
import numeral from 'numeral';

export default class Product extends Component {
    renderHeading() {
        return (
            <div className="panel-heading">
                <h3>{this.props.status} - {this.props.provider__title}, {this.props.product__title} - Effective Rate: {numeral(this.props.rate).format('0,0[.]00')}%</h3>
            </div>
        )
    }

    renderSwitchProductPane() {
        return (
            <div className="col-md-3">
                <p>You could earn</p>
                <h2>+ £{numeral(this.props.switch__product__increase).format('0,0[.]00')}</h2>
                <p>by switching to <b>{this.props.switch__product__title}</b></p>
                <button className="btn btn-success btn-block">Apply Now</button>
            </div>
        )
    }

    renderBody() {

        var switchProductPane = this.props.switch__product__increase > 0 ? this.renderSwitchProductPane() : null;

        return (
            <div className="row">
                <div className="col-md-3">
                    <p><b>Account Name: {this.props.product__title}</b></p>
                    <p><b>Account Type: {this.props.product__type}</b></p>
                    <p><b>Last Reported Balance: £{numeral(this.props.balance).format('0,0[.]00')}</b></p>
                    <p><b>Effective Interest Rate: {numeral(this.props.rate).format('0,0[.]00')}%</b></p>
                    <button className="btn btn-primary">Edit</button>
                    <button className="btn btn-danger">Delete</button>
                </div>
                <div className="col-md-5">

                </div>
                {switchProductPane}
            </div>
        )
    }

    renderCreateBody() {
        return (
            <div className="row">

            </div>
        )
    }

    renderEditBody() {
        return (
            <div className="row">

            </div>
        )
    }

    render() {

        if (this.props.creating) {
            return (
                <div className="panel panel-default">
                    {this.renderHeading()}
                    <div className="panel-body">
                        <div className="container-fluid">
                            {this.renderCreateBody()}
                        </div>
                    </div>
                </div>
            )
        } else if (this.props.editing) {
            return (
                <div className="panel panel-default">
                    {this.renderHeading()}
                    <div className="panel-body">
                        <div className="container-fluid">
                            {this.renderEditBody()}
                        </div>
                    </div>
                </div>
            )
        } else {
            return (
                <div className="panel panel-default">
                    {this.renderHeading()}
                    <div className="panel-body">
                        <div className="container-fluid">
                            {this.renderBody()}
                        </div>
                    </div>
                </div>
            )
        }

    }
}

Product.proptypes = {
    id: PropTypes.string.isRequired,
    status: PropTypes.string.isRequired,
    provider__title: PropTypes.string.isRequired,
    product__title: PropTypes.string.isRequired,
    balance: PropTypes.number.isRequired,
    rate: PropTypes.number.isRequired,
    switch__product__title: PropTypes.string.isRequired,
    switch__product__increase: PropTypes.number.isRequired,
    switch__product__id: PropTypes.string.isRequired
};