use soroban_sdk::{Address, BytesN, Env, String,  xdr::ToXdr};
use crate::{CSAMembership, ShareSize, validate};

pub fn enroll_membership(
    env: Env,
    farm_id: BytesN<32>,
    season: String,
    share_size: ShareSize,
    pickup_location: String,
    start_date: u64,
    end_date: u64,
    member: Address
) {
    member.require_auth();
    validate::validate_season(&env, farm_id.clone(), season.clone(), start_date, end_date);

    let member_xdr = member.clone().to_xdr(&env); // Usar clone para evitar mover member
    let mut member_array = [0u8; 32];
    member_xdr.copy_into_slice(&mut member_array);
    let member_bytesn = BytesN::from_array(&env, &member_array);

    let membership = CSAMembership {
        farm_id,
        season,
        share_size,
        pickup_location,
        start_date,
        end_date,
        member: member_bytesn,
    };

    let token_id = BytesN::from_array(&env, &[0; 32]); // Simplificado, usar hash real en producción
    env.storage().persistent().set(&token_id, &membership);

    env.events().publish(("enroll_membership", "success"), (&member, &token_id));
}