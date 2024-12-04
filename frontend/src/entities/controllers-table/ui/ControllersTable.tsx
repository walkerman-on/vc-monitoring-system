import React, { FC } from 'react';
import { Table } from "shared/ui/table"

interface DataType {
	key: string;
	controller_name: string;
	status: string;
}
interface ITable {
	columns: any,
	data: any,
}

export const ControllersTable: FC<ITable> = ({ columns, data }) => {
	return (
		<Table
			columns={columns}
			dataSource={data}
			bordered
		/>
	);
};
