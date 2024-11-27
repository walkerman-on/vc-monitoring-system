import { FC, memo } from 'react';
import { ITableProps } from './IProps';
import { Table as ANTDTable } from "antd"

export const Table: FC<ITableProps> = memo((props) => {
	return (
		<ANTDTable {...props} />
	);
});