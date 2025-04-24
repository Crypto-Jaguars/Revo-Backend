/* eslint-disable prettier/prettier */
import { Entity, Column, PrimaryGeneratedColumn } from 'typeorm';

@Entity()
export class Metrics {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  metricType: string;

  @Column('decimal')
  value: number;

  @Column('date')
  date: Date;
}
