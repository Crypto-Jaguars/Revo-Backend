import { Entity, Column, PrimaryGeneratedColumn } from 'typeorm';

@Entity('ProductImage')
export class ProductImage {
  @PrimaryGeneratedColumn()
  media_id: number;

  @Column()
  media_key: string;

  @Column()
  format: string;

  @Column()
  size: number;
}
