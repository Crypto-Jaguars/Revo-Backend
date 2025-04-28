use soroban_sdk::{Address, Env, String, BytesN, xdr::ToXdr};
use crate::CSAMembership;

pub fn update_pickup_location(env: Env, token_id: BytesN<32>, new_location: String, member: Address) {
    member.require_auth();
    let mut membership: CSAMembership = env.storage().persistent().get(&token_id)
        .expect("Membership not found");

    let member_xdr = member.clone().to_xdr(&env); // Usar clone para evitar mover member
    let mut member_array = [0u8; 32];
    member_xdr.copy_into_slice(&mut member_array);
    let member_bytesn = BytesN::from_array(&env, &member_array);

    if membership.member != member_bytesn {
        panic!("Unauthorized");
    }

    membership.pickup_location = new_location;
    env.storage().persistent().set(&token_id, &membership);
    env.events().publish(("update_pickup_location", "success"), (&member, &token_id));
}