import React, { useState, useEffect } from 'react';
import { Container, Paper } from '@material-ui/core'
// // import Paper from '@mui/material/Paper';
// import {
//     SelectionState,
//     PagingState,
//     IntegratedPaging,
//     IntegratedSelection,
// } from '@devexpress/dx-react-grid';
// import {
//     Grid,
//     Table,
//     TableHeaderRow,
//     TableSelection,
//     PagingPanel,
// } from '@devexpress/dx-react-grid-material-ui';

import { getProducts } from '../services/product'


// Docs for Grid 
// API Reference: https://devexpress.github.io/devextreme-reactive/react/grid/docs/guides/plugin-overview/

export default function Products() {

    // const [columns] = useState([
    //     { name: 'id', title: 'ID' },
    //     { name: 'display_name', title: 'Name' },
    //     { name: 'file_name', title: 'File' },
    // ]);

    // const [selection, setSelection] = useState([]);

    const [products, setProducts] = useState([]);

    useEffect(() => {
        getProducts().then((res) => setProducts(res));
        console.log(products)
    }, []);

    return (
        <Container>
            <Paper>
                {/* <Grid
                    rows={products}
                    columns={columns}
                >
                    <PagingState
                        defaultCurrentPage={0}
                        pageSize={6}
                    />
                    <SelectionState
                        selection={selection}
                        onSelectionChange={setSelection}
                    />
                    <IntegratedPaging />
                    <IntegratedSelection />
                    <Table />
                    <TableHeaderRow />
                    <TableSelection showSelectAll />
                    <PagingPanel />
                </Grid> */}
            </Paper>
        </Container>
    )
}
