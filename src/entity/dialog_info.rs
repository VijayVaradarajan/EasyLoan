use chrono::{DateTime, FixedOffset};
use sea_orm::entity::prelude::*;
use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, PartialEq, Eq, DeriveEntityModel, Deserialize, Serialize)]
#[sea_orm(table_name = "dialog_info")]
pub struct Model {
    #[sea_orm(primary_key, auto_increment = false)]
    pub dialog_id: i64,
    #[sea_orm(index)]
    pub uid: i64,
    #[serde(skip_deserializing)]
    pub kb_id: i64,
    pub dialog_name: String,
    pub history: String,

    #[serde(skip_deserializing)]
    pub created_at: DateTime<FixedOffset>,
    #[serde(skip_deserializing)]
    pub updated_at: DateTime<FixedOffset>,
    #[serde(skip_deserializing)]
    pub is_deleted: bool
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveRelation)]
pub enum Relation {}

impl Related<super::kb_info::Entity> for Entity {
    fn to() -> RelationDef {
        super::dialog2_kb::Relation::KbInfo.def()
    }

    fn via() -> Option<RelationDef> {
        Some(super::dialog2_kb::Relation::DialogInfo.def().rev())
    }
}

impl ActiveModelBehavior for ActiveModel {}