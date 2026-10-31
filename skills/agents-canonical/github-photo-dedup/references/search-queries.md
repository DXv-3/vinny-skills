# Photo dedup — GitHub search query bank

Replace `LOGIN` with the authenticated user's login from `get_me`.

## Repository search (`search_repositories`)

### Personal

```
user:LOGIN dedup photo
user:LOGIN dedupe image
user:LOGIN duplicate picture
user:LOGIN perceptual hash
user:LOGIN imagededup
user:LOGIN imagehash
user:LOGIN "duplicate image"
user:LOGIN "photo dedup"
user:LOGIN topic:deduplication
```

### Global — high recall

```
(photo OR image OR picture) (dedup OR dedupe OR deduplication OR duplicate)
topic:deduplication
(perceptual OR phash OR pHash OR dhash OR imagehash OR imagededup) (photo OR image)
"duplicate photo"
"duplicate image"
"near duplicate" image
"find duplicate" (photo OR image)
"remove duplicate" (photo OR image)
photo dedup in:name,description,readme
image dedup in:name,description,readme
image-dedup in:name
photo-dedup in:name
duplicate-image in:name
duplicate-photo in:name
```

### Global — quality filters

```
stars:>50 (dedup OR duplicate) (image OR photo)
stars:>10 imagededup
stars:>10 perceptual hash image
fork:false archived:false (dedup OR duplicate) (image OR photo)
language:python (imagededup OR imagehash OR duplicate) image
language:rust duplicate image
language:go perceptual hash
```

### Known libraries / tools (seed discovery)

```
imagededup in:name,description
ImageHash python duplicate
opencv duplicate image detection
pillow perceptual hash
facebook copy detection image
```

## Code search (`search_code`) — max 256 chars

```
imagededup language:python
ImageHash duplicate language:python
phash duplicate image
perceptual_hash duplicate
find_duplicate_images
remove_duplicate_photos
user:LOGIN imagededup
user:LOGIN ImageHash
user:LOGIN "duplicate" path:README.md image
```

## Negative filters (when results are noisy)

Add to queries:

```
NOT database NOT sql NOT kafka NOT stream
```

Use when results skew toward data pipeline "deduplication".