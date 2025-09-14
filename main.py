from __future__ import annotations

import os
import socket
from datetime import datetime

from typing import Dict, List
from uuid import UUID

from fastapi import FastAPI, HTTPException
from fastapi import Query, Path
from typing import Optional

from models.person import PersonCreate, PersonRead, PersonUpdate
from models.address import AddressCreate, AddressRead, AddressUpdate
from models.health import Health

from models.owner import OwnerCreate, OwnerRead, OwnerUpdate
from models.pet import PetCreate, PetRead, PetUpdate

port = int(os.environ.get("FASTAPIPORT", 8000))

# -----------------------------------------------------------------------------
# Fake in-memory "databases"
# -----------------------------------------------------------------------------
persons: Dict[UUID, PersonRead] = {}
addresses: Dict[UUID, AddressRead] = {}
owners: Dict[UUID, OwnerRead] = {}
pets: Dict[UUID, PetRead] = {}
# -----------------------------------------------------------------------------

app = FastAPI(
    title="Person/Address API",
    description="Demo FastAPI app using Pydantic v2 models for Person and Address",
    version="0.1.0",
)

# -----------------------------------------------------------------------------
# Address endpoints
# -----------------------------------------------------------------------------

def make_health(echo: Optional[str], path_echo: Optional[str]=None) -> Health:
    return Health(
        status=200,
        status_message="OK",
        timestamp=datetime.utcnow().isoformat() + "Z",
        ip_address=socket.gethostbyname(socket.gethostname()),
        echo=echo,
        path_echo=path_echo
    )

@app.get("/health", response_model=Health)
def get_health_no_path(echo: str | None = Query(None, description="Optional echo string")):
    # Works because path_echo is optional in the model
    return make_health(echo=echo, path_echo=None)

@app.get("/health/{path_echo}", response_model=Health)
def get_health_with_path(
    path_echo: str = Path(..., description="Required echo in the URL path"),
    echo: str | None = Query(None, description="Optional echo string"),
):
    return make_health(echo=echo, path_echo=path_echo)

@app.post("/addresses", response_model=AddressRead, status_code=201)
def create_address(address: AddressCreate):
    if address.id in addresses:
        raise HTTPException(status_code=400, detail="Address with this ID already exists")
    addresses[address.id] = AddressRead(**address.model_dump())
    return addresses[address.id]

@app.get("/addresses", response_model=List[AddressRead])
def list_addresses(
    street: Optional[str] = Query(None, description="Filter by street"),
    city: Optional[str] = Query(None, description="Filter by city"),
    state: Optional[str] = Query(None, description="Filter by state/region"),
    postal_code: Optional[str] = Query(None, description="Filter by postal code"),
    country: Optional[str] = Query(None, description="Filter by country"),
):
    results = list(addresses.values())

    if street is not None:
        results = [a for a in results if a.street == street]
    if city is not None:
        results = [a for a in results if a.city == city]
    if state is not None:
        results = [a for a in results if a.state == state]
    if postal_code is not None:
        results = [a for a in results if a.postal_code == postal_code]
    if country is not None:
        results = [a for a in results if a.country == country]

    return results

@app.get("/addresses/{address_id}", response_model=AddressRead)
def get_address(address_id: UUID):
    if address_id not in addresses:
        raise HTTPException(status_code=404, detail="Address not found")
    return addresses[address_id]

@app.patch("/addresses/{address_id}", response_model=AddressRead)
def update_address(address_id: UUID, update: AddressUpdate):
    if address_id not in addresses:
        raise HTTPException(status_code=404, detail="Address not found")
    stored = addresses[address_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))
    addresses[address_id] = AddressRead(**stored)
    return addresses[address_id]

# -----------------------------------------------------------------------------
# Person endpoints
# -----------------------------------------------------------------------------
@app.post("/persons", response_model=PersonRead, status_code=201)
def create_person(person: PersonCreate):
    # Each person gets its own UUID; stored as PersonRead
    person_read = PersonRead(**person.model_dump())
    persons[person_read.id] = person_read
    return person_read

@app.get("/persons", response_model=List[PersonRead])
def list_persons(
    uni: Optional[str] = Query(None, description="Filter by Columbia UNI"),
    first_name: Optional[str] = Query(None, description="Filter by first name"),
    last_name: Optional[str] = Query(None, description="Filter by last name"),
    email: Optional[str] = Query(None, description="Filter by email"),
    phone: Optional[str] = Query(None, description="Filter by phone number"),
    birth_date: Optional[str] = Query(None, description="Filter by date of birth (YYYY-MM-DD)"),
    city: Optional[str] = Query(None, description="Filter by city of at least one address"),
    country: Optional[str] = Query(None, description="Filter by country of at least one address"),
):
    results = list(persons.values())

    if uni is not None:
        results = [p for p in results if p.uni == uni]
    if first_name is not None:
        results = [p for p in results if p.first_name == first_name]
    if last_name is not None:
        results = [p for p in results if p.last_name == last_name]
    if email is not None:
        results = [p for p in results if p.email == email]
    if phone is not None:
        results = [p for p in results if p.phone == phone]
    if birth_date is not None:
        results = [p for p in results if str(p.birth_date) == birth_date]

    # nested address filtering
    if city is not None:
        results = [p for p in results if any(addr.city == city for addr in p.addresses)]
    if country is not None:
        results = [p for p in results if any(addr.country == country for addr in p.addresses)]

    return results

@app.get("/persons/{person_id}", response_model=PersonRead)
def get_person(person_id: UUID):
    if person_id not in persons:
        raise HTTPException(status_code=404, detail="Person not found")
    return persons[person_id]

@app.patch("/persons/{person_id}", response_model=PersonRead)
def update_person(person_id: UUID, update: PersonUpdate):
    if person_id not in persons:
        raise HTTPException(status_code=404, detail="Person not found")
    stored = persons[person_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))
    persons[person_id] = PersonRead(**stored)
    return persons[person_id]

# -----------------------------------------------------------------------------
# Owner endpoints
# -----------------------------------------------------------------------------
@app.post("/owners", response_model=OwnerRead, status_code=201)
def create_owner(owner: OwnerCreate):
    # Each owner gets its own UUID; stored as OwnerRead
    owner_read = OwnerRead(**owner.model_dump())
    owners[owner_read.id] = owner_read
    return owner_read

@app.get("/owners", response_model=List[OwnerRead])
def list_owners(
    first_name: Optional[str] = Query(None, description="Filter by first name"),
    last_name: Optional[str] = Query(None, description="Filter by last name"),
    email: Optional[str] = Query(None, description="Filter by email"),
    phone: Optional[str] = Query(None, description="Filter by phone number"),
    birth_date: Optional[str] = Query(None, description="Filter by date of birth (YYYY-MM-DD)"),
    city: Optional[str] = Query(None, description="Filter by city of at least one address"),
    country: Optional[str] = Query(None, description="Filter by country of at least one address"),
):
    results = list(owners.values())

    if first_name is not None:
        results = [o for o in results if o.first_name == first_name]
    if last_name is not None:
        results = [o for o in results if o.last_name == last_name]
    if email is not None:
        results = [o for o in results if o.email == email]
    if phone is not None:
        results = [o for o in results if o.phone == phone]
    if birth_date is not None:
        results = [o for o in results if str(o.birth_date) == birth_date]

    # nested address filtering
    if city is not None:
        results = [o for o in results if any(addr.city == city for addr in o.addresses)]
    if country is not None:
        results = [o for o in results if any(addr.country == country for addr in o.addresses)]

    return results

@app.get("/owners/{owner_id}", response_model=OwnerRead)
def get_owner(owner_id: UUID):
    if owner_id not in owners:
        raise HTTPException(status_code=404, detail="Owner not found")
    return owners[owner_id]

@app.patch("/owners/{owner_id}", response_model=OwnerRead)
def update_owner(owner_id: UUID, update: OwnerUpdate):
    if owner_id not in owners:
        raise HTTPException(status_code=404, detail="Owner not found")
    stored = owners[owner_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))
    owners[owner_id] = OwnerRead(**stored)
    return owners[owner_id]

@app.delete("/owners/{owner_id}", status_code=204)
def delete_owner(owner_id: UUID):
    if owner_id not in owners:
        raise HTTPException(status_code=404, detail="Owner not found")
    del owners[owner_id]
    return None


# -----------------------------------------------------------------------------
# Pet endpoints
# -----------------------------------------------------------------------------
@app.post("/pets", response_model=PetRead, status_code=201)
def create_pet(pet: PetCreate):
    # Each pet gets its own UUID; stored as PetRead
    pet_read = PetRead(**pet.model_dump())
    pets[pet_read.id] = pet_read
    return pet_read     
@app.get("/pets", response_model=List[PetRead])
def list_pets(
    name: Optional[str] = Query(None, description="Filter by pet name"),
    species: Optional[str] = Query(None, description="Filter by species"),
    age: Optional[int] = Query(None, description="Filter by age"),
    weight: Optional[float] = Query(None, description="Filter by weight"),
):
    results = list(pets.values())

    if name is not None:
        results = [p for p in results if p.name == name]
    if species is not None:
        results = [p for p in results if p.species == species]
    if age is not None:
        results = [p for p in results if p.age == age]
    if weight is not None:
        results = [p for p in results if p.weight == weight]

    return results  
@app.get("/pets/{pet_id}", response_model=PetRead)
def get_pet(pet_id: UUID):
    if pet_id not in pets:
        raise HTTPException(status_code=404, detail="Pet not found")
    return pets[pet_id]     
@app.patch("/pets/{pet_id}", response_model=PetRead)
def update_pet(pet_id: UUID, update: PetUpdate):        
    if pet_id not in pets:
        raise HTTPException(status_code=404, detail="Pet not found")
    stored = pets[pet_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))
    pets[pet_id] = PetRead(**stored)
    return pets[pet_id]
@app.delete("/pets/{pet_id}", status_code=204)
def delete_pet(pet_id: UUID):
    if pet_id not in pets:
        raise HTTPException(status_code=404, detail="Pet not found")
    del pets[pet_id]
    return None     

    

# -----------------------------------------------------------------------------
# Root
# -----------------------------------------------------------------------------
@app.get("/")
def root():
    return {"message": "Welcome to the Person/Address API. See /docs for OpenAPI UI."}

# -----------------------------------------------------------------------------
# Entrypoint for `python main.py`
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
