DELETE FROM `s1`.`client_receipt`;
INSERT INTO `s1`.`client_receipt`
(`id`,
`receipt_number`,
`trans_date`,
`staff_id`,
`trans_biz_loc`,
`coordinator_name`,
`client_names`,
`event_date`,
`receipt_amount_php`,
`last_amend_date`,
`unpaid_balance_php`,
`is_final`,
`created_on`,
`created_by`,
`updated_on`,
`updated_by`)
SELECT
`id`,
`receipt_number`,
`trans_date`,
`staff_id`,
`trans_biz_loc`,
`coordinator_name`,
`client_names`,
`event_date`,
`receipt_amount_php`,
`last_amend_date`,
`unpaid_balance_php`,
`is_final`,
`created_on`,
`created_by`,
`updated_on`,
`updated_by`
FROM client_receipt_20220525;
RENAME TABLE client_receipt_20220525 TO client_receipt_20220525_1;